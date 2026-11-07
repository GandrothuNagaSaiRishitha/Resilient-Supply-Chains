"""Purchase order and shipment tracking endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import CurrentContext, audit, get_current_context
from ..models import PurchaseOrder, ShipmentEvent, Supplier
from ..schemas import OrderCreate, OrderUpdate, ShipmentEventCreate
from ..services import memory as memory_service
from ..services import metrics as metrics_service
from ..services import monitoring
from .common import event_json, get_order_or_404, order_json, supplier_metrics

router = APIRouter(tags=["orders"])


def _next_order_number(db: Session, organization_id: uuid.UUID) -> str:
    year = datetime.now(timezone.utc).year
    count = db.scalar(
        select(func.count(PurchaseOrder.id)).where(PurchaseOrder.organization_id == organization_id)
    )
    candidate = f"PO-{year}-{1000 + int(count or 0) + 1}"
    while db.scalar(
        select(PurchaseOrder.id).where(
            PurchaseOrder.organization_id == organization_id,
            PurchaseOrder.order_number == candidate,
        )
    ):
        count = int(count or 0) + 1
        candidate = f"PO-{year}-{1000 + count + 1}"
    return candidate


def _supplier_name_map(db: Session, organization_id: uuid.UUID) -> dict[uuid.UUID, str]:
    return {
        s.id: s.name
        for s in db.scalars(select(Supplier).where(Supplier.organization_id == organization_id)).all()
    }


@router.get("/orders")
def list_orders(
    status_filter: str | None = Query(default=None, alias="status"),
    supplier_id: uuid.UUID | None = None,
    search: str | None = None,
    priority: str | None = None,
    limit: int = Query(default=200, ge=1, le=500),
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    stmt = select(PurchaseOrder).where(PurchaseOrder.organization_id == ctx.organization.id)
    if status_filter:
        stmt = stmt.where(PurchaseOrder.status == status_filter)
    if supplier_id:
        stmt = stmt.where(PurchaseOrder.supplier_id == supplier_id)
    if priority:
        stmt = stmt.where(PurchaseOrder.priority == priority)
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                PurchaseOrder.order_number.ilike(pattern),
                PurchaseOrder.product.ilike(pattern),
                PurchaseOrder.destination.ilike(pattern),
            )
        )
    orders = db.scalars(stmt.order_by(PurchaseOrder.order_date.desc()).limit(limit)).all()
    names = _supplier_name_map(db, ctx.organization.id)
    metrics = supplier_metrics(db, ctx.organization.id)
    return {
        "count": len(orders),
        "orders": [
            order_json(o, names.get(o.supplier_id), metrics.get(o.supplier_id)) for o in orders
        ],
        "synthetic_demo_data": True,
    }


@router.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    request: Request,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    supplier = db.get(Supplier, payload.supplier_id)
    if supplier is None or supplier.organization_id != ctx.organization.id:
        raise HTTPException(status_code=404, detail="Supplier not found")

    order = PurchaseOrder(
        organization_id=ctx.organization.id,
        supplier_id=supplier.id,
        order_number=payload.order_number or _next_order_number(db, ctx.organization.id),
        product=payload.product.strip(),
        quantity=payload.quantity,
        order_date=payload.order_date or datetime.now(timezone.utc),
        promised_date=payload.promised_date,
        estimated_arrival=payload.estimated_arrival or payload.promised_date,
        actual_arrival=payload.actual_arrival,
        status=payload.status,
        priority=payload.priority,
        destination=payload.destination,
        transport_mode=payload.transport_mode,
        tracking_reference=payload.tracking_reference,
        financial_impact=payload.financial_impact,
        notes=payload.notes,
        synthetic=False,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    monitoring.schedule_order_monitoring(db, order)
    audit(
        db,
        ctx.organization.id,
        ctx.user.id,
        "order.create",
        "purchase_order",
        str(order.id),
        {"order_number": order.order_number, "supplier": supplier.name},
        request.client.host if request.client else None,
    )
    db.commit()
    metrics = supplier_metrics(db, ctx.organization.id)
    return order_json(order, supplier.name, metrics.get(supplier.id))


@router.get("/orders/{order_id}")
def get_order(
    order_id: uuid.UUID,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    order = get_order_or_404(db, ctx.organization, order_id)
    supplier = db.get(Supplier, order.supplier_id)
    metrics = supplier_metrics(db, ctx.organization.id)
    payload = order_json(order, supplier.name if supplier else None, metrics.get(order.supplier_id))
    events = db.scalars(
        select(ShipmentEvent)
        .where(ShipmentEvent.order_id == order.id, ShipmentEvent.organization_id == ctx.organization.id)
        .order_by(ShipmentEvent.event_date)
    ).all()
    payload["shipment_events"] = [event_json(e) for e in events]
    return payload


@router.patch("/orders/{order_id}")
def update_order(
    order_id: uuid.UUID,
    payload: OrderUpdate,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    order = get_order_or_404(db, ctx.organization, order_id)
    changes = payload.model_dump(exclude_unset=True)
    if "supplier_id" in changes:
        supplier = db.get(Supplier, changes["supplier_id"])
        if supplier is None or supplier.organization_id != ctx.organization.id:
            raise HTTPException(status_code=404, detail="Supplier not found")
    previous_status = order.status
    for key, value in changes.items():
        setattr(order, key, value)
    if changes.get("status") == "delivered" and order.actual_arrival is None:
        order.actual_arrival = datetime.now(timezone.utc)
    db.commit()
    db.refresh(order)
    if "status" in changes or "promised_date" in changes:
        monitoring.reschedule_order_monitoring(db, order)

    retained = False
    if order.status == "delivered" and previous_status != "delivered":
        supplier = db.get(Supplier, order.supplier_id)
        content = (
            f"Verified outcome for order {order.order_number} from {supplier.name if supplier else 'supplier'}: "
            f"promised {order.promised_date.date().isoformat()}, delivered "
            f"{order.actual_arrival.date().isoformat() if order.actual_arrival else 'unknown'}, "
            f"delay {metrics_service.delay_days(order)} days. Product {order.product}, "
            f"quantity {order.quantity}."
        )
        try:
            memory_service.retain(
                db,
                ctx.organization,
                content=content,
                category="outcome",
                source_type="verified_business_fact",
                supplier_id=order.supplier_id,
                order_id=order.id,
                event_date=order.actual_arrival,
                context="delivery outcome",
            )
            retained = True
        except Exception:  # noqa: BLE001
            retained = False

    audit(
        db,
        ctx.organization.id,
        ctx.user.id,
        "order.update",
        "purchase_order",
        str(order.id),
        {"changes": {k: str(v) for k, v in changes.items()}, "outcome_retained": retained},
    )
    db.commit()
    supplier = db.get(Supplier, order.supplier_id)
    metrics = supplier_metrics(db, ctx.organization.id)
    result = order_json(order, supplier.name if supplier else None, metrics.get(order.supplier_id))
    result["outcome_retained_in_hindsight"] = retained
    return result


@router.get("/orders/{order_id}/events")
def list_order_events(
    order_id: uuid.UUID,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    order = get_order_or_404(db, ctx.organization, order_id)
    events = db.scalars(
        select(ShipmentEvent)
        .where(ShipmentEvent.order_id == order.id, ShipmentEvent.organization_id == ctx.organization.id)
        .order_by(ShipmentEvent.event_date)
    ).all()
    return {
        "order_id": str(order.id),
        "order_number": order.order_number,
        "count": len(events),
        "events": [event_json(e) for e in events],
    }


@router.post("/orders/{order_id}/events", status_code=status.HTTP_201_CREATED)
def create_order_event(
    order_id: uuid.UUID,
    payload: ShipmentEventCreate,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    order = get_order_or_404(db, ctx.organization, order_id)
    event = ShipmentEvent(
        organization_id=ctx.organization.id,
        order_id=order.id,
        event_type=payload.event_type,
        event_date=payload.event_date or datetime.now(timezone.utc),
        location=payload.location,
        description=payload.description,
        source=payload.source,
        synthetic=False,
    )
    db.add(event)
    if payload.event_type in {"delay", "customs_hold", "disruption"} and order.status not in {
        "delivered",
        "cancelled",
    }:
        order.status = "delayed"
    db.commit()
    db.refresh(event)
    audit(
        db,
        ctx.organization.id,
        ctx.user.id,
        "shipment.event_create",
        "shipment_event",
        str(event.id),
        {"order_number": order.order_number, "event_type": event.event_type},
    )
    db.commit()
    return event_json(event)


@router.get("/shipments")
def shipment_board(
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    """Live shipment tracking view: open orders with their latest event."""
    orders = db.scalars(
        select(PurchaseOrder)
        .where(
            PurchaseOrder.organization_id == ctx.organization.id,
            PurchaseOrder.status.in_(["created", "confirmed", "processing", "dispatched", "in_transit", "delayed"]),
        )
        .order_by(PurchaseOrder.promised_date)
    ).all()
    names = _supplier_name_map(db, ctx.organization.id)
    metrics = supplier_metrics(db, ctx.organization.id)
    tracking = []
    for order in orders:
        events = db.scalars(
            select(ShipmentEvent)
            .where(ShipmentEvent.order_id == order.id)
            .order_by(ShipmentEvent.event_date.desc())
        ).all()
        latest = events[0] if events else None
        tracking.append(
            {
                **order_json(order, names.get(order.supplier_id), metrics.get(order.supplier_id)),
                "latest_event": event_json(latest) if latest else None,
                "event_count": len(events),
            }
        )
    return {
        "count": len(tracking),
        "shipments": tracking,
        "synthetic_demo_data": True,
        "note": "Shipment events are stored records; the AI never invents a tracking update.",
    }
