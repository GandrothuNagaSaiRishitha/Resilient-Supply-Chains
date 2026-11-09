"""Runtime settings, integration status and health."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..deps import CurrentContext, get_current_context
from ..models import MemoryOperationLog, Supplier, User
from ..services import memory as memory_service

logger = logging.getLogger("supplymind.settings")
router = APIRouter(tags=["settings"])
settings = get_settings()


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    database_ok = False
    db_error = None
    try:
        db.execute(text("SELECT 1"))
        database_ok = True
    except Exception as exc:  # noqa: BLE001
        logger.error("database health check failed", exc_info=exc)

    hindsight_ok = False
    hindsight_version = None
    hindsight_error = None
    client = memory_service._client(timeout=min(settings.hindsight_timeout_seconds, 5.0))
    try:
        enclosed = client.get_version()
        hindsight_version = str(enclosed)[:200]
        hindsight_ok = True
    except Exception as exc:  # noqa: BLE001
        logger.error("Hindsight health check failed", exc_info=exc)
    finally:
        memory_service._close_client(client)

    return {
        "status": "ok" if database_ok and hindsight_ok else "degraded",
        "database": {"ok": database_ok, "status": "available" if database_ok else "unavailable"},
        "hindsight": {
            "ok": hindsight_ok,
            "status": "available" if hindsight_ok else "unavailable",
            "version": hindsight_version,
        },
        "groq_configured": bool(settings.groq_api_key),
        "band_configured": bool(settings.band_enabled),
        "scheduler_enabled": settings.scheduler_enabled,
    }


@router.get("/settings")
def get_runtime_settings(
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    supplier_count = len(
        db.scalars(select(Supplier).where(Supplier.organization_id == ctx.organization.id)).all()
    )
    memory_logs = db.scalars(
        select(MemoryOperationLog)
        .where(MemoryOperationLog.organization_id == ctx.organization.id)
        .order_by(MemoryOperationLog.created_at.desc())
        .limit(1)
    ).all()
    return {
        "organization": {
            "id": str(ctx.organization.id),
            "name": ctx.organization.name,
            "slug": ctx.organization.slug,
            "is_demo": ctx.organization.is_demo,
            "memory_bank_id": ctx.organization.memory_bank_id,
            "supplier_count": supplier_count,
        },
        "user": {
            "id": str(ctx.user.id),
            "email": ctx.user.email,
            "full_name": ctx.user.full_name,
            "role": ctx.user.role,
        },
        "models": {
            "primary": settings.groq_model,
            "fallback": settings.groq_fallback_model,
            "max_tool_iterations": settings.agent_max_tool_iterations,
            "max_retries": settings.agent_max_retries,
        },
        "integrations": {
            "groq": {"configured": bool(settings.groq_api_key), "label": "Groq tool calling"},
            "hindsight": {
                "configured": True,
                "base_url": settings.hindsight_base_url,
                "engine": "Hindsight (self-hosted)",
                "last_operation": memory_logs[0].created_at.isoformat() if memory_logs else None,
            },
            "band": {
                "configured": bool(settings.band_enabled),
                "enabled": settings.band_enabled,
                "note": (
                    "Optional Band collaboration integration. It is disabled because no Band agent "
                    "credentials are configured. Core features do not depend on Band."
                ),
            },
        },
        "scheduler": {
            "enabled": settings.scheduler_enabled,
            "interval_seconds": settings.scheduler_interval_seconds,
        },
        "data_policy": {
            "demo_dataset": "synthetic and labeled",
            "memory_reset": "demo organization only",
        },
    }
