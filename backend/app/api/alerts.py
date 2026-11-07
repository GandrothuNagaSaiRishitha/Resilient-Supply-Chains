"""Alerts and persistent scheduled actions."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import CurrentContext, audit, get_current_context
from ..models import Alert, ScheduledAction, Supplier
from ..schemas import AlertUpdate

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _alert_json(alert: Alert, supplier_name: str | None = None) -> dict:
    return {
        "id": str(alert.id),
        "order_id": str(alert.order_id) if alert.order_id else None,
        "supplier_id": str(alert.supplier_id) if alert.supplier_id else None,
        "supplier_name": supplier_name,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "title": alert.title,
        "message": alert.message,
        "status": alert.status,
        "due_at": alert.due_at.isoformat() if alert.due_at else None,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        "synthetic": alert.synthetic,
    }


@router.get("")
def list_alerts(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=500),
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    stmt = select(Alert).where(Alert.organization_id == ctx.organization.id)
    if status_filter:
        stmt = stmt.where(Alert.status == status_filter)
    alerts = db.scalars(stmt.order_by(Alert.created_at.desc()).limit(limit)).all()
    names = {
        s.id: s.name
        for s in db.scalars(select(Supplier).where(Supplier.organization_id == ctx.organization.id)).all()
    }
    return {
        "count": len(alerts),
        "open_count": len([a for a in alerts if a.status == "open"]),
        "alerts": [_alert_json(a, names.get(a.supplier_id)) for a in alerts],
    }


@router.patch("/{alert_id}")
def update_alert(
    alert_id: uuid.UUID,
    payload: AlertUpdate,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    alert = db.get(Alert, alert_id)
    if alert is None or alert.organization_id != ctx.organization.id:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = payload.status
    now = datetime.now(timezone.utc)
    if payload.status == "acknowledged":
        alert.acknowledged_at = now
    elif payload.status in {"resolved", "dismissed"}:
        alert.resolved_at = now
    db.commit()
    db.refresh(alert)
    audit(
        db,
        ctx.organization.id,
        ctx.user.id,
        "alert.update",
        "alert",
        str(alert.id),
        {"status": payload.status},
    )
    db.commit()
    return _alert_json(alert)


@router.get("/scheduled-actions")
def scheduled_actions(
    status_filter: str | None = Query(default=None, alias="status"),
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    stmt = select(ScheduledAction).where(ScheduledAction.organization_id == ctx.organization.id)
    if status_filter:
        stmt = stmt.where(ScheduledAction.status == status_filter)
    rows = db.scalars(stmt.order_by(ScheduledAction.run_at).limit(200)).all()
    return {
        "count": len(rows),
        "actions": [
            {
                "id": str(a.id),
                "order_id": str(a.order_id) if a.order_id else None,
                "action_type": a.action_type,
                "run_at": a.run_at.isoformat() if a.run_at else None,
                "status": a.status,
                "attempts": a.attempts,
                "last_error": a.last_error,
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            }
            for a in rows
        ],
    }
