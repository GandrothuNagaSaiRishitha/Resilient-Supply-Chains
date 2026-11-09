"""Crisis reporting endpoints."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_context, CurrentContext, audit
from ..models import Organization, Supplier, PurchaseOrder, SupplyChainIncident, User
from ..schemas_incidents import CrisisReportCreate

router = APIRouter(prefix="/crises", tags=["crises"])

CRISIS_TYPE_ALIASES = {
    "Shipment Disruption": "Shipment Disruption",
    "Supplier Failure": "Supplier Failure",
    "Inventory Shortage": "Inventory Shortage",
}
URGENCY_ALIASES = {"Low": "Low", "Medium": "Medium", "High": "High", "Critical": "Critical"}


def _next_incident_number(db: Session, org_id: uuid.UUID) -> str:
    prefix = f"INC-{org_id.hex[:8].upper()}"
    for _ in range(5):
        max_num = db.scalar(
            select(func.max(SupplyChainIncident.incident_number)).where(
                SupplyChainIncident.organization_id == org_id,
                SupplyChainIncident.incident_number.like(f"{prefix}-%"),
            )
        )
        next_seq = 1
        if max_num:
            try:
                next_seq = int(max_num.split("-")[-1]) + 1
            except ValueError:
                next_seq = 1
        candidate = f"{prefix}-{next_seq:04d}"
        exists = db.scalar(
            select(SupplyChainIncident.id).where(
                SupplyChainIncident.organization_id == org_id,
                SupplyChainIncident.incident_number == candidate,
            )
        )
        if not exists:
            return candidate
    raise HTTPException(status_code=409, detail="Could not generate a unique incident number")


@router.get("/form-options")
def form_options(ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db)):
    suppliers = db.scalars(
        select(Supplier).where(Supplier.organization_id == ctx.organization.id).order_by(Supplier.name)
    ).all()
    orders = db.scalars(
        select(PurchaseOrder)
        .where(
            PurchaseOrder.organization_id == ctx.organization.id,
            PurchaseOrder.status.notin_(["delivered", "cancelled"]),
        )
        .order_by(PurchaseOrder.order_number)
    ).all()
    return {
        "data": {
            "crisisTypes": ["Shipment Disruption", "Supplier Failure", "Inventory Shortage"],
            "urgencies": ["Low", "Medium", "High", "Critical"],
            "suppliers": [{"id": str(s.id), "name": s.name} for s in suppliers],
            "orders": [
                {
                    "id": str(order.id),
                    "orderNumber": order.order_number,
                    "supplierId": str(order.supplier_id),
                    "product": order.product,
                    "status": order.status,
                    "destination": order.destination,
                }
                for order in orders
            ],
        }
    }


@router.post("")
def create_crisis(
    payload: CrisisReportCreate,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    org_id = ctx.organization.id
    supplier = None
    if payload.supplier_id:
        try:
            supplier_id = uuid.UUID(payload.supplier_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid supplier id")
        supplier = db.get(Supplier, supplier_id)
        if supplier is None or supplier.organization_id != org_id:
            raise HTTPException(status_code=422, detail="Supplier not found in this organization")
    order = None
    if payload.shipment_id:
        try:
            shipment_id = uuid.UUID(payload.shipment_id)
        except ValueError:
            shipment_id = None
        if shipment_id:
            order = db.get(PurchaseOrder, shipment_id)
        else:
            order = db.scalar(
                select(PurchaseOrder).where(
                    PurchaseOrder.organization_id == org_id,
                    PurchaseOrder.order_number == payload.shipment_id.strip(),
                    PurchaseOrder.supplier_id == supplier.id,
                )
            )
        if (
            order is None
            or order.organization_id != org_id
            or order.supplier_id != supplier.id
        ):
            raise HTTPException(status_code=422, detail="Linked shipment/order not found in this organization")

    incident_number = _next_incident_number(db, org_id)
    incident = SupplyChainIncident(
        organization_id=org_id,
        incident_number=incident_number,
        crisis_type=payload.crisis_type,
        title=payload.incident_title,
        description=payload.description,
        supplier_id=supplier.id if supplier else None,
        order_id=order.id if order else None,
        product_component=order.product if order else payload.product_component,
        origin=payload.origin,
        destination=payload.destination,
        expected_delay_days=payload.expected_delay_days,
        available_inventory_quantity=payload.available_inventory_quantity,
        affected_orders=payload.affected_orders,
        urgency=payload.urgency,
        incident_date=payload.incident_date,
        status="open",
        reported_by=ctx.user.id,
        synthetic=False,
    )
    db.add(incident)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Incident number conflict; please retry")
    audit(
        db,
        org_id,
        ctx.user.id,
        "crisis.report",
        "supply_chain_incident",
        str(incident.id),
        {"incident_number": incident_number, "crisis_type": payload.crisis_type},
    )
    db.commit()
    db.refresh(incident)
    return {"data": {"incidentId": str(incident.id), "demo": False, "message": "Crisis report recorded successfully."}}
