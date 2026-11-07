"""Database-backed proactive monitoring.

Scheduled actions live in PostgreSQL, so they survive application restarts.
A lightweight APScheduler tick claims due actions and creates idempotent alerts.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Alert, Organization, PurchaseOrder, ScheduledAction, Supplier
from . import metrics as metrics_service

logger = logging.getLogger("supplymind.monitoring")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _add_action(
    db: Session,
    org_id: uuid.UUID,
    order_id: uuid.UUID,
    action_type: str,
    run_at: datetime,
    dedupe_key: str,
    payload: dict | None = None,
) -> ScheduledAction | None:
    existing = db.scalar(
        select(ScheduledAction).where(
            ScheduledAction.organization_id == org_id,
            ScheduledAction.dedupe_key == dedupe_key,
        )
    )
    if existing:
        return existing
    action = ScheduledAction(
        organization_id=org_id,
        order_id=order_id,
        action_type=action_type,
        run_at=run_at,
        dedupe_key=dedupe_key,
        payload=payload or {},
    )
    db.add(action)
    return action


def schedule_order_monitoring(db: Session, order: PurchaseOrder) -> list[ScheduledAction]:
    """Create a risk-aware monitoring schedule for a newly created order."""
    supplier = db.get(Supplier, order.supplier_id)
    promised = _aware(order.promised_date)
    avg_delay = 0.0
    if supplier:
        m = metrics_service.compute_supplier_metrics(
            supplier,
            [o for o in supplier.orders if o.organization_id == order.organization_id] if supplier.orders else [],
            [],
            [],
        )
        avg_delay = max(0.0, m.avg_delay_days)

    # A risk-management checkpoint, not a guaranteed delivery prediction.
    checkpoint_days_before = max(2, int(round(avg_delay)) + 2)
    checkpoint = promised - timedelta(days=checkpoint_days_before)
    if checkpoint < _now():
        checkpoint = _now() + timedelta(minutes=1)

    created: list[ScheduledAction] = []
    key_prefix = f"order:{order.id}:v1"
    plan = [
        ("risk_checkpoint", checkpoint, f"{key_prefix}:checkpoint", {"avg_delay": avg_delay}),
        ("supplier_confirmation", promised - timedelta(days=2), f"{key_prefix}:confirm", {"avg_delay": avg_delay}),
        ("overdue_check", promised + timedelta(hours=12), f"{key_prefix}:overdue", {"avg_delay": avg_delay}),
        (
            "escalation",
            promised + timedelta(days=max(3, int(round(avg_delay)) + 3)),
            f"{key_prefix}:escalation",
            {"avg_delay": avg_delay},
        ),
    ]
    for action_type, run_at, dedupe, payload in plan:
        if run_at < _now():
            # keep already-past checkpoints actionable immediately
            run_at = _now() + timedelta(seconds=30)
        action = _add_action(db, order.organization_id, order.id, action_type, run_at, dedupe, payload)
        if action:
            created.append(action)
    db.commit()
    return created


def reschedule_order_monitoring(db: Session, order: PurchaseOrder) -> None:
    """Cancel pending actions and rebuild the schedule after a material change."""
    pending = db.scalars(
        select(ScheduledAction).where(
            ScheduledAction.order_id == order.id,
            ScheduledAction.status == "pending",
        )
    ).all()
    for action in pending:
        action.status = "cancelled"
    db.commit()
    if order.status not in {"delivered", "cancelled"}:
        schedule_order_monitoring(db, order)


def create_alert(
    db: Session,
    org_id: uuid.UUID,
    *,
    order_id: uuid.UUID | None,
    supplier_id: uuid.UUID | None,
    alert_type: str,
    severity: str,
    title: str,
    message: str,
    dedupe_key: str,
    due_at: datetime | None = None,
    synthetic: bool = False,
) -> Alert | None:
    existing = db.scalar(
        select(Alert).where(Alert.organization_id == org_id, Alert.dedupe_key == dedupe_key)
    )
    if existing:
        return existing
    alert = Alert(
        organization_id=org_id,
        order_id=order_id,
        supplier_id=supplier_id,
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        dedupe_key=dedupe_key,
        due_at=due_at,
        synthetic=synthetic,
    )
    db.add(alert)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return db.scalar(
            select(Alert).where(Alert.organization_id == org_id, Alert.dedupe_key == dedupe_key)
        )
    db.refresh(alert)
    return alert


def _execute_action(db: Session, action: ScheduledAction) -> None:
    order = db.get(PurchaseOrder, action.order_id) if action.order_id else None
    org = db.get(Organization, action.organization_id)
    if not org:
        action.status = "failed"
        action.last_error = "organization missing"
        db.commit()
        return

    if not order:
        action.status = "completed"
        action.completed_at = _now()
        db.commit()
        return

    if order.status in {"delivered", "cancelled"}:
        action.status = "cancelled"
        action.completed_at = _now()
        db.commit()
        return

    supplier = db.get(Supplier, order.supplier_id)
    supplier_name = supplier.name if supplier else "the supplier"
    avg_delay = float(action.payload.get("avg_delay", 0) or 0)
    promised = _aware(order.promised_date)
    dedupe = f"alert:{action.dedupe_key}"

    if action.action_type == "risk_checkpoint":
        create_alert(
            db,
            org.id,
            order_id=order.id,
            supplier_id=order.supplier_id,
            alert_type="upcoming_delivery_checkpoint",
            severity="medium",
            title=f"Delivery checkpoint: {order.order_number}",
            message=(
                f"{supplier_name} promised this order for {promised.date().isoformat()}. "
                f"Historical average delay for this supplier is {avg_delay:.1f} days. "
                "Ask for a dated confirmation now so a contingency can be activated early. "
                "This is a risk checkpoint, not a guaranteed delivery prediction."
            ),
            dedupe_key=dedupe,
            due_at=promised,
        )
    elif action.action_type == "supplier_confirmation":
        create_alert(
            db,
            org.id,
            order_id=order.id,
            supplier_id=order.supplier_id,
            alert_type="supplier_confirmation_reminder",
            severity="medium",
            title=f"Confirm delivery: {order.order_number}",
            message=f"Request written confirmation from {supplier_name} for the {promised.date().isoformat()} delivery.",
            dedupe_key=dedupe,
            due_at=promised,
        )
    elif action.action_type == "overdue_check":
        late_by = (_now() - promised).total_seconds() / 86400.0
        if late_by <= 0:
            action.status = "completed"
            action.completed_at = _now()
            db.commit()
            return
        order.status = "delayed"
        create_alert(
            db,
            org.id,
            order_id=order.id,
            supplier_id=order.supplier_id,
            alert_type="overdue_order",
            severity="high",
            title=f"Overdue order: {order.order_number}",
            message=(
                f"{supplier_name} is {late_by:.1f} days past the promised date. "
                "Open a recovery request and evaluate a qualified alternative supplier."
            ),
            dedupe_key=dedupe,
            due_at=promised,
        )
    elif action.action_type == "escalation":
        create_alert(
            db,
            org.id,
            order_id=order.id,
            supplier_id=order.supplier_id,
            alert_type="risk_escalation",
            severity="critical",
            title=f"Escalation required: {order.order_number}",
            message=(
                f"The order remains open past the supplier's historical delay buffer ({avg_delay:.1f} days). "
                "Escalate to the procurement manager and activate a contingency source."
            ),
            dedupe_key=dedupe,
            due_at=promised,
        )

    action.status = "completed"
    action.completed_at = _now()
    action.attempts += 1
    db.commit()


def process_due_actions(db: Session, now: datetime | None = None) -> dict:
    now = now or _now()
    due = db.scalars(
        select(ScheduledAction)
        .where(ScheduledAction.status == "pending", ScheduledAction.run_at <= now)
        .order_by(ScheduledAction.run_at)
        .limit(100)
    ).all()
    processed = 0
    errors = 0
    for action in due:
        try:
            _execute_action(db, action)
            processed += 1
        except Exception as exc:  # noqa: BLE001
            errors += 1
            logger.exception("scheduled action failed: %s", action.id)
            action.status = "failed"
            action.attempts += 1
            action.last_error = str(exc)[:2000]
            db.commit()
    return {"processed": processed, "errors": errors, "due": len(due)}


def scan_overdue_orders(db: Session, organization_id: uuid.UUID | None = None) -> int:
    """Mark open orders past their promised date as delayed and schedule alerts."""
    now = _now()
    stmt = select(PurchaseOrder).where(
        PurchaseOrder.status.in_(["created", "confirmed", "processing", "dispatched", "in_transit"]),
        PurchaseOrder.promised_date < now,
    )
    if organization_id:
        stmt = stmt.where(PurchaseOrder.organization_id == organization_id)
    orders = db.scalars(stmt).all()
    for order in orders:
        order.status = "delayed"
        create_alert(
            db,
            order.organization_id,
            order_id=order.id,
            supplier_id=order.supplier_id,
            alert_type="overdue_order",
            severity="high",
            title=f"Order overdue: {order.order_number}",
            message="The promised delivery date has passed and the order is still open.",
            dedupe_key=f"scan:overdue:{order.id}",
            due_at=_aware(order.promised_date),
        )
    db.commit()
    return len(orders)


def tick() -> dict:
    db = SessionLocal()
    try:
        result = process_due_actions(db)
        return result
    finally:
        db.close()


_scheduler = None


def start_scheduler(interval_seconds: int = 60) -> None:
    global _scheduler
    if _scheduler is not None:
        return
    from apscheduler.schedulers.background import BackgroundScheduler

    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        tick,
        "interval",
        seconds=interval_seconds,
        id="supplymind-monitoring-tick",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    logger.info("monitoring scheduler started (every %ss)", interval_seconds)


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
