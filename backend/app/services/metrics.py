"""Deterministic supply-chain metrics.

All authoritative numbers are calculated here from PostgreSQL records. The LLM
may explain these numbers but never computes them itself.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import (
    InventoryItem,
    PurchaseOrder,
    QualityIncident,
    ShipmentEvent,
    Supplier,
    SupplierComplaint,
)
from ..schemas import SupplierMetrics

OPEN_STATUSES = {"created", "confirmed", "processing", "dispatched", "in_transit", "delayed"}
CLOSED_STATUSES = {"delivered", "cancelled"}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def ensure_aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def delay_days(order: PurchaseOrder, reference: datetime | None = None) -> float | None:
    promised = ensure_aware(order.promised_date)
    actual = ensure_aware(order.actual_arrival)
    if promised is None:
        return None
    if actual is not None:
        return round((actual - promised).total_seconds() / 86400.0, 2)
    if reference is None:
        reference = now_utc()
    if order.status in OPEN_STATUSES:
        return round((reference - promised).total_seconds() / 86400.0, 2)
    return None


def is_on_time(order: PurchaseOrder) -> bool:
    d = delay_days(order)
    return d is not None and d <= 0.49


def compute_supplier_metrics(
    supplier: Supplier,
    orders: Iterable[PurchaseOrder],
    complaints: Iterable[SupplierComplaint],
    incidents: Iterable[QualityIncident],
    reference: datetime | None = None,
) -> SupplierMetrics:
    reference = reference or now_utc()
    orders = list(orders)
    complaints = list(complaints)
    incidents = list(incidents)

    delivered = [o for o in orders if o.actual_arrival is not None or o.status == "delivered"]
    delays = [delay_days(o, reference) for o in delivered]
    delays = [d for d in delays if d is not None]
    on_time = [d for d in delays if d <= 0.49]

    open_orders = [o for o in orders if o.status in OPEN_STATUSES]
    late_open = [o for o in open_orders if (ensure_aware(o.promised_date) or reference) < reference]

    quality = sum(1 for c in complaints if c.complaint_type == "quality") + len(incidents)
    comms = sum(1 for c in complaints if c.complaint_type == "communication")
    transport = sum(1 for c in complaints if c.complaint_type == "transportation")

    avg_delay = round(mean(delays), 2) if delays else 0.0
    max_delay = round(max(delays), 2) if delays else 0.0
    on_time_rate = round(len(on_time) / len(delays), 4) if delays else 0.0
    late_rate = 1.0 - on_time_rate if delays else 0.0

    # Transparent reliability formula (documented in MEMORY_DESIGN / README).
    penalty = (
        min(40.0, max(0.0, avg_delay) * 4.0)
        + min(30.0, late_rate * 30.0)
        + min(20.0, quality * 5.0)
        + min(10.0, comms * 3.0)
        + min(10.0, transport * 2.0)
    )
    reliability = round(max(0.0, min(100.0, 100.0 - penalty)), 1)

    return SupplierMetrics(
        delivered_orders=len(delivered),
        avg_delay_days=avg_delay,
        max_delay_days=max_delay,
        on_time_rate=on_time_rate,
        reliability_score=reliability,
        quality_complaints=quality,
        communication_complaints=comms,
        transportation_incidents=transport,
        open_orders=len(open_orders),
        late_open_orders=len(late_open),
    )


def supplier_metrics_map(db: Session, organization_id: uuid.UUID) -> dict[uuid.UUID, SupplierMetrics]:
    suppliers = db.scalars(select(Supplier).where(Supplier.organization_id == organization_id)).all()
    orders = db.scalars(select(PurchaseOrder).where(PurchaseOrder.organization_id == organization_id)).all()
    complaints = db.scalars(
        select(SupplierComplaint).where(SupplierComplaint.organization_id == organization_id)
    ).all()
    incidents = db.scalars(
        select(QualityIncident).where(QualityIncident.organization_id == organization_id)
    ).all()

    by_supplier_orders: dict[uuid.UUID, list[PurchaseOrder]] = defaultdict(list)
    for order in orders:
        by_supplier_orders[order.supplier_id].append(order)
    by_supplier_complaints: dict[uuid.UUID, list[SupplierComplaint]] = defaultdict(list)
    for complaint in complaints:
        by_supplier_complaints[complaint.supplier_id].append(complaint)
    by_supplier_incidents: dict[uuid.UUID, list[QualityIncident]] = defaultdict(list)
    for incident in incidents:
        by_supplier_incidents[incident.supplier_id].append(incident)

    return {
        s.id: compute_supplier_metrics(
            s,
            by_supplier_orders[s.id],
            by_supplier_complaints[s.id],
            by_supplier_incidents[s.id],
        )
        for s in suppliers
    }


def risk_level_for(order: PurchaseOrder, metrics: SupplierMetrics | None) -> str:
    if order.status in CLOSED_STATUSES:
        return "closed"
    d = delay_days(order)
    score = 100.0
    if metrics:
        score = metrics.reliability_score
    if d is not None and d > 0:
        score -= min(50.0, d * 8.0)
    if order.priority == "critical":
        score -= 15.0
    elif order.priority == "high":
        score -= 8.0
    if score >= 80:
        return "low"
    if score >= 60:
        return "medium"
    if score >= 40:
        return "high"
    return "critical"


def dashboard(db: Session, organization_id: uuid.UUID) -> dict:
    reference = now_utc()
    suppliers = db.scalars(select(Supplier).where(Supplier.organization_id == organization_id)).all()
    orders = db.scalars(
        select(PurchaseOrder).where(PurchaseOrder.organization_id == organization_id)
    ).all()
    metrics = supplier_metrics_map(db, organization_id)

    active = [o for o in orders if o.status in OPEN_STATUSES]
    delivered = [o for o in orders if o.status == "delivered" or o.actual_arrival is not None]
    delayed = [o for o in orders if o.status == "delayed" or (o.status in OPEN_STATUSES and (delay_days(o, reference) or 0) > 0)]
    at_risk = [o for o in active if risk_level_for(o, metrics.get(o.supplier_id)) in {"high", "critical"}]
    delays = [d for d in (delay_days(o, reference) for o in delivered) if d is not None]
    upcoming = [
        o for o in active if 0 <= ((ensure_aware(o.promised_date) - reference).total_seconds() / 86400) <= 14
    ]

    from ..models import Alert  # local import avoids cycles

    pending_alerts = db.scalars(
        select(Alert).where(Alert.organization_id == organization_id, Alert.status.in_(["open", "acknowledged"]))
    ).all()

    status_distribution = {s: 0 for s in ["created", "confirmed", "processing", "dispatched", "in_transit", "delayed", "delivered", "cancelled"]}
    for o in orders:
        status_distribution[o.status] = status_distribution.get(o.status, 0) + 1

    on_time_count = sum(1 for o in delivered if is_on_time(o))
    late_count = max(0, len(delivered) - on_time_count)

    # Delay trend by ISO month for delivered orders.
    trend: dict[str, list[float]] = defaultdict(list)
    for o in delivered:
        d = delay_days(o)
        if d is None:
            continue
        key = (ensure_aware(o.promised_date) or reference).strftime("%Y-%m")
        trend[key].append(d)
    delay_trend = [
        {"month": k, "avg_delay_days": round(mean(v), 2), "orders": len(v)}
        for k, v in sorted(trend.items())
    ]

    supplier_rows = []
    for s in suppliers:
        m = metrics.get(s.id)
        if not m:
            continue
        supplier_rows.append(
            {
                "id": str(s.id),
                "name": s.name,
                "reliability_score": m.reliability_score,
                "on_time_rate": m.on_time_rate,
                "avg_delay_days": m.avg_delay_days,
                "delivered_orders": m.delivered_orders,
                "open_orders": m.open_orders,
                "quality_complaints": m.quality_complaints,
            }
        )
    supplier_rows.sort(key=lambda x: x["reliability_score"], reverse=True)

    risk_distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for o in active:
        risk_distribution[risk_level_for(o, metrics.get(o.supplier_id))] = (
            risk_distribution.get(risk_level_for(o, metrics.get(o.supplier_id)), 0) + 1
        )

    return {
        "synthetic_demo_data": True,
        "generated_at": reference.isoformat(),
        "kpis": {
            "active_orders": len(active),
            "delivered_orders": len(delivered),
            "delayed_orders": len(delayed),
            "at_risk_orders": len(at_risk),
            "avg_delivery_delay_days": round(mean(delays), 2) if delays else 0.0,
            "supplier_reliability_avg": round(mean([m.reliability_score for m in metrics.values()]), 1) if metrics else 0.0,
            "upcoming_deliveries_14d": len(upcoming),
            "pending_alerts": len(pending_alerts),
            "critical_bottlenecks": len([o for o in active if risk_level_for(o, metrics.get(o.supplier_id)) == "critical"]),
            "suppliers": len(suppliers),
            "total_orders": len(orders),
        },
        "charts": {
            "on_time_vs_delayed": [
                {"name": "On time", "value": on_time_count},
                {"name": "Delayed", "value": late_count},
            ],
            "supplier_reliability": supplier_rows,
            "delay_trend": delay_trend,
            "status_distribution": [{"status": k, "count": v} for k, v in status_distribution.items()],
            "risk_distribution": [{"risk": k, "count": v} for k, v in risk_distribution.items()],
        },
        "upcoming_deliveries": [
            {
                "id": str(o.id),
                "order_number": o.order_number,
                "supplier": next((s.name for s in suppliers if s.id == o.supplier_id), "Unknown"),
                "promised_date": ensure_aware(o.promised_date).isoformat(),
                "priority": o.priority,
                "status": o.status,
            }
            for o in sorted(upcoming, key=lambda x: ensure_aware(x.promised_date))[:8]
        ],
    }


def bottlenecks(db: Session, organization_id: uuid.UUID) -> list[dict]:
    reference = now_utc()
    suppliers = {s.id: s for s in db.scalars(select(Supplier).where(Supplier.organization_id == organization_id)).all()}
    orders = db.scalars(select(PurchaseOrder).where(PurchaseOrder.organization_id == organization_id)).all()
    metrics = supplier_metrics_map(db, organization_id)
    complaints = db.scalars(select(SupplierComplaint).where(SupplierComplaint.organization_id == organization_id)).all()
    incidents = db.scalars(select(QualityIncident).where(QualityIncident.organization_id == organization_id)).all()
    events = db.scalars(select(ShipmentEvent).where(ShipmentEvent.organization_id == organization_id)).all()
    inventory = db.scalars(select(InventoryItem).where(InventoryItem.organization_id == organization_id)).all()

    results: list[dict] = []
    by_supplier: dict[uuid.UUID, list[PurchaseOrder]] = defaultdict(list)
    for o in orders:
        by_supplier[o.supplier_id].append(o)

    def base(supplier_id: uuid.UUID, kind: str, severity: str, title: str, message: str, affected: list[PurchaseOrder], evidence: list[str], impact: float, action: str):
        supplier = suppliers.get(supplier_id)
        m = metrics.get(supplier_id)
        results.append(
            {
                "kind": kind,
                "severity": severity,
                "title": title,
                "message": message,
                "supplier_id": str(supplier_id),
                "supplier": supplier.name if supplier else "Unknown",
                "affected_orders": [
                    {"id": str(o.id), "order_number": o.order_number, "status": o.status, "promised_date": ensure_aware(o.promised_date).isoformat()}
                    for o in affected
                ],
                "historical_evidence": evidence,
                "business_impact": round(impact, 2),
                "recommended_intervention": action,
                "metrics": m.model_dump() if m else {},
                "deterministic": True,
            }
        )

    # Rule 1: overdue open orders.
    for supplier_id, supplier_orders in by_supplier.items():
        overdue = [o for o in supplier_orders if o.status in OPEN_STATUSES and (ensure_aware(o.promised_date) or reference) < reference]
        if overdue:
            impact = sum(o.financial_impact for o in overdue)
            sev = "critical" if len(overdue) >= 3 or impact >= 100000 else "high" if len(overdue) >= 2 else "medium"
            base(
                supplier_id,
                "overdue_orders",
                sev,
                f"{len(overdue)} overdue order(s) with {suppliers[supplier_id].name}",
                "Orders remain open after their promised delivery date.",
                overdue,
                [f"{o.order_number} promised {ensure_aware(o.promised_date).date().isoformat()} and is still {o.status}" for o in overdue],
                impact,
                "Contact the supplier for a dated recovery plan and prepare a qualified backup source.",
            )

    # Rule 2: repeated late delivery pattern.
    for supplier_id, m in metrics.items():
        if m.delivered_orders >= 3 and m.on_time_rate <= 0.5:
            sup_orders = [o for o in by_supplier.get(supplier_id, []) if o.actual_arrival is not None]
            base(
                supplier_id,
                "repeated_delivery_failures",
                "high" if m.avg_delay_days < 5 else "critical",
                f"Repeated delivery failures: {suppliers[supplier_id].name}",
                f"Only {round(m.on_time_rate*100)}% of {m.delivered_orders} delivered orders arrived on time; average delay {m.avg_delay_days} days.",
                sup_orders[-5:],
                [f"Average delay {m.avg_delay_days} days across {m.delivered_orders} delivered orders" for _ in range(1)],
                sum(o.financial_impact for o in by_supplier.get(supplier_id, []) if o.status in OPEN_STATUSES),
                "Shift routine volume to a more reliable supplier and require milestone confirmations for critical orders.",
            )

    # Rule 3: supplier concentration.
    total_active = len([o for o in orders if o.status in OPEN_STATUSES])
    for supplier_id, supplier_orders in by_supplier.items():
        active = [o for o in supplier_orders if o.status in OPEN_STATUSES]
        if total_active >= 3 and len(active) >= 3 and len(active) / total_active >= 0.4:
            base(
                supplier_id,
                "supplier_concentration",
                "high",
                f"Supplier concentration risk: {suppliers[supplier_id].name}",
                f"{len(active)} of {total_active} active orders depend on this supplier.",
                active,
                [f"{len(active)} active orders, {round(100*len(active)/total_active)}% of the open book"],
                sum(o.financial_impact for o in active),
                "Qualify a second source and split the open book to reduce single-supplier exposure.",
            )

    # Rule 4: quality / communication evidence.
    for supplier_id, m in metrics.items():
        if m.quality_complaints >= 2 or m.communication_complaints >= 2:
            base(
                supplier_id,
                "supplier_quality_or_communication",
                "high" if m.quality_complaints >= 3 else "medium",
                f"Quality or communication issues: {suppliers[supplier_id].name}",
                f"{m.quality_complaints} quality complaint/incident(s) and {m.communication_complaints} communication complaint(s) on record.",
                [o for o in by_supplier.get(supplier_id, []) if o.status in OPEN_STATUSES],
                [c.description for c in complaints if c.supplier_id == supplier_id][:4],
                0.0,
                "Require corrective-action evidence before awarding the next critical order.",
            )

    # Rule 5: transportation disruptions in last 30 days.
    disruptions = [e for e in events if e.event_type in {"delay", "incident", "customs_hold", "disruption"} and ensure_aware(e.event_date) >= reference - timedelta(days=30)]
    if disruptions:
        affected_ids = {e.order_id for e in disruptions}
        affected = [o for o in orders if o.id in affected_ids]
        supplier_id = affected[0].supplier_id if affected else next(iter(suppliers))
        base(
            supplier_id,
            "transportation_disruption",
            "high",
            "Recent transportation disruptions",
            f"{len(disruptions)} disruption event(s) recorded in the last 30 days.",
            affected,
            [f"{e.event_type}: {e.description}" for e in disruptions[:4]],
            sum(o.financial_impact for o in affected),
            "Add transit buffer and validate an alternate route or carrier.",
        )

    # Rule 6: critical inventory below reorder point.
    for item in inventory:
        if item.quantity_on_hand <= item.reorder_point:
            base(
                item.supplier_id or next(iter(suppliers)),
                "critical_inventory",
                "critical" if item.criticality == "critical" else "high",
                f"Low inventory: {item.name}",
                f"On hand {item.quantity_on_hand}, reorder point {item.reorder_point}.",
                [o for o in by_supplier.get(item.supplier_id, []) if o.status in OPEN_STATUSES],
                [f"{item.sku} stock {item.quantity_on_hand} <= reorder point {item.reorder_point}"],
                item.quantity_on_hand * item.unit_cost,
                "Expedite replenishment and confirm the next inbound receipt.",
            )

    results.sort(key=lambda r: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(r["severity"], 4))
    return results
