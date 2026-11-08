"""Impact analysis computed from persisted tenant orders and inventory."""
from __future__ import annotations
import uuid
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import CurrentContext, get_current_context
from ..models import PurchaseOrder, Supplier, SupplyChainIncident
from .common import inventory_for_component

router = APIRouter(prefix="/impacts", tags=["impact-analysis"])

def _severity(value: str) -> str:
    return value if value in {"Low", "Medium", "High", "Critical"} else "Medium"

def _incident(row: SupplyChainIncident) -> dict:
    return {"id": str(row.id), "crisisType": row.crisis_type, "title": row.title,
            "reportedAt": row.created_at.isoformat() if row.created_at else row.incident_date.isoformat()}

def _analysis(row: SupplyChainIncident, db: Session, org_id: uuid.UUID) -> dict:
    severity = _severity(row.urgency)
    q = select(PurchaseOrder).where(PurchaseOrder.organization_id == org_id,
        PurchaseOrder.status.notin_(["delivered", "cancelled"]))
    if row.order_id: q = q.where(PurchaseOrder.id == row.order_id)
    elif row.supplier_id: q = q.where(PurchaseOrder.supplier_id == row.supplier_id)
    orders = db.scalars(q.order_by(PurchaseOrder.promised_date).limit(200)).all()
    supplier = (
        db.scalar(
            select(Supplier).where(
                Supplier.id == row.supplier_id,
                Supplier.organization_id == org_id,
            )
        )
        if row.supplier_id
        else None
    )
    inventory = inventory_for_component(db, org_id, row.supplier_id, row.product_component)
    shortage = sum(max(0, i.reorder_point - i.quantity_on_hand) for i in inventory)
    exposure = sum(o.financial_impact for o in orders)
    delay = row.expected_delay_days or 0
    products = [{"id":str(i.id),"product":i.name,"component":i.category,"supplier":supplier.name if supplier else "Unassigned",
        "shortage":max(0,i.reorder_point-i.quantity_on_hand),"severity":severity} for i in inventory]
    if not products:
        products = [{"id":str(row.id),"product":row.product_component,"component":row.product_component,
            "supplier":supplier.name if supplier else "Unassigned","shortage":0,"severity":severity}]
    customers = [{"id":str(o.id),"customer":o.destination or "Unspecified destination","orderValue":o.financial_impact,
        "priority":_severity(o.priority.title()),"expectedDelayDays":delay} for o in orders]
    warehouses = [{"id":str(i.id),"warehouse":i.name,"location":"Location not recorded",
        "availableInventory":i.quantity_on_hand,"inventoryAtRisk":max(0,i.reorder_point-i.quantity_on_hand),
        "coverageDays":0,"severity":severity} for i in inventory]
    counts = Counter([severity] * max(1, len(orders) + len(products)))
    return {"incident":_incident(row),"kpis":[
        {"id":"orders","label":"Open orders at risk","value":len(orders),"formattedValue":str(len(orders)),"severity":severity},
        {"id":"inventory","label":"Units below reorder point","value":shortage,"formattedValue":str(shortage),"severity":severity},
        {"id":"delay","label":"Expected delay","value":delay,"unit":"days","formattedValue":f"{delay} days","severity":severity},
        {"id":"financial","label":"Recorded order exposure","value":exposure,"unit":"currency","formattedValue":f"{exposure:,.2f}","severity":severity}],
        "affectedProducts":products,"warehouseImpacts":warehouses,"customerOrders":customers,
        "distribution":[{"category":"Inventory","value":len(products)},{"category":"Orders","value":len(orders)},
            {"category":"Transportation","value":1 if row.crisis_type == "Shipment Disruption" else 0},
            {"category":"Supplier","value":1 if row.supplier_id else 0}],
        "severityIndicators":[{"severity":level,"count":counts.get(level,0),
            "description":f"{counts.get(level,0)} linked records assessed at {level.lower()} severity"}
            for level in ["Critical","High","Medium","Low"]],
        "assumptions":{"items":["Analysis uses records belonging to this organization only.",
            "Financial exposure sums the recorded financial_impact on linked open purchase orders; it is not a revenue forecast.",
            "The current schema has no warehouse-location or consumption-rate fields, so warehouse location and coverage days are not inferred.",
            "When an order is linked, only that order is assessed; otherwise open orders are matched by supplier."]}}

@router.get("/incidents")
def impact_incidents(ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(SupplyChainIncident).where(SupplyChainIncident.organization_id == ctx.organization.id).order_by(SupplyChainIncident.incident_date.desc())).all()
    return {"data":[_incident(r) for r in rows]}

@router.get("/incidents/{incident_id}")
def impact_analysis(incident_id: uuid.UUID, ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db)) -> dict:
    row = db.scalar(select(SupplyChainIncident).where(SupplyChainIncident.id == incident_id, SupplyChainIncident.organization_id == ctx.organization.id))
    if row is None: raise HTTPException(status_code=404, detail="Incident not found")
    return {"data":_analysis(row, db, ctx.organization.id)}
