"""Recovery simulation scenarios and strategy confirmation."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_context, CurrentContext, audit
from ..models import (
    PurchaseOrder,
    Supplier,
    SupplyChainIncident,
    RecoveryConfirmation,
    User,
)
from ..schemas_incidents import RecoveryConfirmationCreate
from ..services import metrics as metrics_service
from .common import inventory_for_component

router = APIRouter(prefix="/recovery-simulations", tags=["recovery-simulations"])

STRATEGIES = [
    ("wait", "Wait and Monitor"),
    ("reroute", "Reroute Shipments"),
    ("emergency-sourcing", "Emergency Sourcing"),
    ("redistribute", "Redistribute Inventory"),
]


def _severity_label(score: float) -> str:
    if score >= 75:
        return "Low"
    if score >= 55:
        return "Medium"
    if score >= 35:
        return "High"
    return "Critical"


def _incident_row(row: SupplyChainIncident) -> dict:
    return {
        "id": str(row.id),
        "crisisType": row.crisis_type,
        "title": row.title,
        "reportedAt": row.created_at.isoformat() if row.created_at else row.incident_date.isoformat(),
    }


def build_scenario(db: Session, org_id: uuid.UUID, row: SupplyChainIncident) -> dict:
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
    metrics = metrics_service.supplier_metrics_map(db, org_id)
    supplier_score = None
    if supplier and supplier.id in metrics:
        supplier_score = metrics[supplier.id].reliability_score

    base_delay = row.expected_delay_days or 0
    order = (
        db.scalar(
            select(PurchaseOrder).where(
                PurchaseOrder.id == row.order_id,
                PurchaseOrder.organization_id == org_id,
            )
        )
        if row.order_id
        else None
    )
    base_cost = float(order.financial_impact) if order else 0.0
    affected_inventory = inventory_for_component(db, org_id, row.supplier_id, row.product_component)
    all_component_inventory = inventory_for_component(db, org_id, None, row.product_component)
    inventory_matched = affected_inventory.status == "matched"
    transferable_inventory_matched = all_component_inventory.status == "matched"
    if not inventory_matched:
        baseline_shortage = None
    elif row.available_inventory_quantity is not None:
        baseline_shortage = sum(
            max(0, item.reorder_point - row.available_inventory_quantity)
            for item in affected_inventory.items
        )
    else:
        baseline_shortage = sum(
            max(0, item.reorder_point - item.quantity_on_hand)
            for item in affected_inventory.items
        )
    transferable_units = (
        sum(
            item.quantity_on_hand - item.reorder_point
            for item in all_component_inventory.items
            if item.supplier_id != row.supplier_id and item.quantity_on_hand > item.reorder_point
        )
        if transferable_inventory_matched
        else None
    )

    strategies = []
    for key, name in STRATEGIES:
        if key == "wait":
            additional_cost = 0.0
            delay = base_delay
            shortage = baseline_shortage
            risk = _severity_label(supplier_score if supplier_score is not None else 50)
            feasible = "Feasible" if base_delay <= 5 else "Conditional"
            note = "No immediate action; monitor for changes. Reliable only when expected delay is small."
            trade_off = "Lowest cost, longest exposure to delay."
        elif key == "reroute":
            additional_cost = round(base_cost * 0.15, 2)
            delay = max(0, base_delay - 3)
            shortage = baseline_shortage
            risk = _severity_label((supplier_score or 50) + 5)
            feasible = "Feasible"
            note = "Change transport route or port to avoid the disruption point."
            trade_off = "Moderate cost for modest delay reduction."
        elif key == "emergency-sourcing":
            additional_cost = round(base_cost * 0.35, 2)
            delay = max(0, base_delay - base_delay)
            shortage = baseline_shortage
            alt_score = None
            for other in db.scalars(
                select(Supplier).where(
                    Supplier.organization_id == org_id,
                    Supplier.id != (supplier.id if supplier else uuid.UUID(int=0)),
                )
            ).all():
                if other.id in metrics and metrics[other.id].reliability_score >= 60:
                    alt_score = metrics[other.id].reliability_score
                    break
            if alt_score is None:
                feasible = "Not feasible"
                note = "No qualified alternative supplier in this organization."
                trade_off = "Fastest recovery but highest cost and supplier risk."
                risk = "Critical"
            else:
                feasible = "Feasible"
                note = "Source from a qualified alternative supplier."
                trade_off = "Highest cost, fastest restoration of supply."
                risk = _severity_label(alt_score)
        else:  # redistribute
            additional_cost = round(base_cost * 0.10, 2)
            delay = max(0, base_delay - 2)
            shortage = (
                max(0, baseline_shortage - transferable_units)
                if baseline_shortage is not None and transferable_units is not None
                else None
            )
            risk = _severity_label((supplier_score or 50) - 5)
            if transferable_units is None:
                feasible = "Conditional"
                note = f"Transfer feasibility is unknown. {all_component_inventory.detail}"
            else:
                feasible = "Conditional" if transferable_units else "Not feasible"
                note = (
                    f"Up to {transferable_units} units are above reorder point at other suppliers; "
                    "transfer capacity and location are not recorded."
                    if transferable_units
                    else "No transferable surplus is recorded for this component."
                )
            trade_off = "Low cost, depends on spare inventory at another site."

        strategies.append(
            {
                "key": key,
                "name": name,
                "summary": note,
                "additionalCost": additional_cost,
                "deliveryDelayDays": delay,
                "projectedShortageUnits": shortage,
                "riskLevel": risk,
                "feasibility": feasible,
                "feasibilityNote": note,
                "tradeOff": trade_off,
            }
        )

    recommended = min(
        strategies,
        key=lambda s: (
            0 if s["feasibility"] == "Feasible" else (1 if s["feasibility"] == "Conditional" else 2),
            s["additionalCost"],
            s["deliveryDelayDays"],
        ),
    )

    supplier_name = supplier.name if supplier else "Unassigned"
    constraints = [
        {"id": "supplier", "label": "Primary supplier", "detail": supplier_name},
        {"id": "urgency", "label": "Urgency", "detail": row.urgency},
        {"id": "expectedDelay", "label": "Expected delay", "detail": f"{base_delay} days"},
        {"id": "orgScope", "label": "Organization scope", "detail": "Only this organization's records are used."},
        {"id": "inventory", "label": "Inventory basis", "detail": f"{baseline_shortage} units below recorded reorder points; transfer capacity is estimated from recorded stock."},
    ]
    summary = (
        f"{row.crisis_type} reported for {row.product_component}. "
        f"Expected delay {base_delay} days; supplier reliability score {supplier_score if supplier_score is not None else 'not assessed'}."
    )

    return {
        "incident": _incident_row(row),
        "summary": summary,
        "constraints": constraints + [
            {"id": "inventoryMapping", "label": "Inventory match", "detail": affected_inventory.detail},
        ],
        "strategies": strategies,
        "recommendedStrategyKey": recommended["key"],
        "recommendationExplanation": (
            f"Recommended '{recommended['name']}' because it is {recommended['feasibility'].lower()} "
            f"with the lowest combined cost and delay among feasible options."
        ),
    }


@router.get("/incidents")
def simulation_incidents(
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    rows = db.scalars(
        select(SupplyChainIncident)
        .where(SupplyChainIncident.organization_id == ctx.organization.id)
        .order_by(SupplyChainIncident.incident_date.desc())
    ).all()
    return {"data": [_incident_row(r) for r in rows]}


@router.get("/incidents/{incident_id}")
def simulation_scenario(
    incident_id: uuid.UUID,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    row = db.scalar(
        select(SupplyChainIncident).where(
            SupplyChainIncident.id == incident_id,
            SupplyChainIncident.organization_id == ctx.organization.id,
        )
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"data": build_scenario(db, ctx.organization.id, row)}


@router.post("/confirmations")
def confirm_strategy(
    payload: RecoveryConfirmationCreate,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    iid = payload.incident_id
    strategy_key = payload.strategy_key
    incident = db.scalar(
        select(SupplyChainIncident).where(
            SupplyChainIncident.id == iid,
            SupplyChainIncident.organization_id == ctx.organization.id,
        )
    )
    if incident is None or incident.organization_id != ctx.organization.id:
        raise HTTPException(status_code=404, detail="Incident not found")

    name = dict(STRATEGIES).get(strategy_key, strategy_key)
    confirmation = RecoveryConfirmation(
        organization_id=ctx.organization.id,
        incident_id=iid,
        strategy_key=strategy_key,
        strategy_name=name,
        confirmed_by=ctx.user.id,
        confirmation_note=None,
        synthetic=False,
    )
    db.add(confirmation)
    audit(
        db,
        ctx.organization.id,
        ctx.user.id,
        "recovery.confirm",
        "recovery_confirmation",
        str(confirmation.id),
        {"incident_id": str(iid), "strategy_key": strategy_key},
    )
    db.commit()
    db.refresh(confirmation)
    return {
        "data": {
            "confirmationId": str(confirmation.id),
            "incidentId": str(iid),
            "strategyKey": strategy_key,
            "message": "Recovery strategy confirmed.",
        }
    }
