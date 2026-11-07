"""Crisis intake and incident lifecycle APIs."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import CurrentContext, audit, get_current_context
from ..models import PurchaseOrder, Supplier, SupplyChainIncident
from ..schemas_incidents import CrisisReportCreate, IncidentStatusUpdate

router = APIRouter(prefix="/crises", tags=["crises"])
TYPES = ["Shipment Disruption", "Supplier Failure", "Inventory Shortage"]
URGENCIES = ["Low", "Medium", "High", "Critical"]

def _json(row: SupplyChainIncident, supplier_name: str | None = None) -> dict:
    return {"incidentId": str(row.id), "incidentNumber": row.incident_number, "crisisType": row.crisis_type,
        "title": row.title, "description": row.description, "supplierId": str(row.supplier_id) if row.supplier_id else None,
        "supplier": supplier_name, "shipmentId": str(row.order_id) if row.order_id else None,
        "productComponent": row.product_component, "origin": row.origin, "destination": row.destination,
        "expectedDelayDays": row.expected_delay_days, "availableInventoryQuantity": row.available_inventory_quantity,
        "affectedOrders": row.affected_orders, "urgency": row.urgency, "incidentDate": row.incident_date.isoformat(),
        "status": row.status, "reportedAt": row.created_at.isoformat() if row.created_at else None,
        "resolvedAt": row.resolved_at.isoformat() if row.resolved_at else None, "synthetic": row.synthetic}

@router.get("/form-options")
def crisis_form_options(ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db)) -> dict:
    suppliers = db.scalars(select(Supplier).where(Supplier.organization_id == ctx.organization.id, Supplier.status == "active").order_by(Supplier.name)).all()
    return {"crisisTypes": TYPES, "suppliers": [{"id": str(s.id), "name": s.name} for s in suppliers], "urgencies": URGENCIES}

@router.post("", status_code=status.HTTP_201_CREATED)
def create_crisis(payload: CrisisReportCreate, request: Request, ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db)) -> dict:
    supplier_id = uuid.UUID(payload.supplier_id) if payload.supplier_id else None
    order_id = uuid.UUID(payload.shipment_id) if payload.shipment_id else None
    supplier = db.get(Supplier, supplier_id) if supplier_id else None
    if supplier_id and (supplier is None or supplier.organization_id != ctx.organization.id):
        raise HTTPException(status_code=404, detail="Supplier not found")
    order = db.get(PurchaseOrder, order_id) if order_id else None
    if order_id and (order is None or order.organization_id != ctx.organization.id):
        raise HTTPException(status_code=404, detail="Shipment/order not found")
    if order and supplier_id and order.supplier_id != supplier_id:
        raise HTTPException(status_code=422, detail="Shipment does not belong to the selected supplier")
    row = SupplyChainIncident(organization_id=ctx.organization.id, incident_number=f"INC-{uuid.uuid4().hex[:10].upper()}",
        crisis_type=payload.crisis_type, title=payload.incident_title.strip(), description=payload.description.strip(),
        supplier_id=supplier_id or (order.supplier_id if order else None), order_id=order_id,
        product_component=payload.product_component.strip(), origin=payload.origin, destination=payload.destination,
        expected_delay_days=payload.expected_delay_days, available_inventory_quantity=payload.available_inventory_quantity,
        affected_orders=payload.affected_orders, urgency=payload.urgency, incident_date=payload.incident_date,
        reported_by=ctx.user.id, synthetic=False)
    db.add(row); db.flush()
    audit(db, ctx.organization.id, ctx.user.id, "crisis.create", "supply_chain_incident", str(row.id),
          {"incident_number": row.incident_number, "crisis_type": row.crisis_type}, request.client.host if request.client else None)
    db.commit(); db.refresh(row)
    return {"incidentId": str(row.id), "demo": False, "message": "Crisis report recorded successfully."}

@router.get("")
def list_crises(ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(SupplyChainIncident).where(SupplyChainIncident.organization_id == ctx.organization.id).order_by(SupplyChainIncident.incident_date.desc())).all()
    suppliers = {s.id: s.name for s in db.scalars(select(Supplier).where(Supplier.organization_id == ctx.organization.id)).all()}
    return {"count": len(rows), "incidents": [_json(r, suppliers.get(r.supplier_id)) for r in rows]}

@router.get("/{incident_id}")
def get_crisis(incident_id: uuid.UUID, ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db)) -> dict:
    row = db.scalar(select(SupplyChainIncident).where(SupplyChainIncident.id == incident_id, SupplyChainIncident.organization_id == ctx.organization.id))
    if row is None: raise HTTPException(status_code=404, detail="Incident not found")
    supplier = db.get(Supplier, row.supplier_id) if row.supplier_id else None
    return _json(row, supplier.name if supplier else None)

@router.patch("/{incident_id}/status")
def update_crisis_status(incident_id: uuid.UUID, payload: IncidentStatusUpdate, ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db)) -> dict:
    row = db.scalar(select(SupplyChainIncident).where(SupplyChainIncident.id == incident_id, SupplyChainIncident.organization_id == ctx.organization.id))
    if row is None: raise HTTPException(status_code=404, detail="Incident not found")
    row.status = payload.status
    row.resolved_at = datetime.now(timezone.utc) if payload.status == "resolved" else None
    audit(db, ctx.organization.id, ctx.user.id, "crisis.status_update", "supply_chain_incident", str(row.id), {"status": row.status})
    db.commit(); db.refresh(row)
    supplier = db.get(Supplier, row.supplier_id) if row.supplier_id else None
    return _json(row, supplier.name if supplier else None)
