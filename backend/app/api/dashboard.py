"""Dashboard and bottleneck endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import CurrentContext, get_current_context
from ..services import metrics as metrics_service

router = APIRouter(tags=["operations"])


@router.get("/dashboard")
def dashboard(
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    return metrics_service.dashboard(db, ctx.organization.id)


@router.get("/bottlenecks")
def bottlenecks(
    severity: str | None = Query(default=None),
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    items = metrics_service.bottlenecks(db, ctx.organization.id)
    if severity:
        items = [i for i in items if i["severity"] == severity]
    return {
        "count": len(items),
        "items": items,
        "synthetic_demo_data": True,
        "note": "Every bottleneck is produced by deterministic rules over PostgreSQL records.",
    }
