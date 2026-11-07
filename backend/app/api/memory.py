"""Organizational memory endpoints backed by a live Hindsight server."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import CurrentContext, audit, get_current_context
from ..models import PurchaseOrder, Supplier
from ..schemas import (
    MemoryRecallRequest,
    MemoryReflectRequest,
    MemoryRetainRequest,
)
from ..services import memory as memory_service

router = APIRouter(prefix="/memory", tags=["memory"])


def _validate_refs(db: Session, ctx: CurrentContext, supplier_id, order_id) -> None:
    if supplier_id:
        supplier = db.get(Supplier, supplier_id)
        if supplier is None or supplier.organization_id != ctx.organization.id:
            raise HTTPException(status_code=404, detail="Supplier not found")
    if order_id:
        order = db.get(PurchaseOrder, order_id)
        if order is None or order.organization_id != ctx.organization.id:
            raise HTTPException(status_code=404, detail="Order not found")


@router.get("/overview")
def overview(
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    return memory_service.overview(db, ctx.organization)


@router.get("/records")
def records(
    limit: int = Query(default=200, ge=1, le=500),
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    rows = memory_service.records(db, ctx.organization, limit=limit)
    return {"count": len(rows), "records": rows}


@router.get("/history")
def history(
    limit: int = Query(default=100, ge=1, le=500),
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    rows = memory_service.history(db, ctx.organization, limit=limit)
    return {"count": len(rows), "operations": rows}


@router.post("/retain")
def retain(
    payload: MemoryRetainRequest,
    request: Request,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    _validate_refs(db, ctx, payload.supplier_id, payload.order_id)
    if payload.source_type == "verified_business_fact" and not (payload.supplier_id or payload.order_id):
        raise HTTPException(
            status_code=422,
            detail="A verified business fact must reference an existing supplier or order",
        )
    try:
        result = memory_service.retain(
            db,
            ctx.organization,
            content=payload.content,
            category=payload.category,
            context=payload.context,
            source_type=payload.source_type,
            supplier_id=payload.supplier_id,
            order_id=payload.order_id,
            event_date=payload.event_date,
            confidence=payload.confidence,
            document_id=payload.document_id,
        )
    except memory_service.HindsightUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    audit(
        db,
        ctx.organization.id,
        ctx.user.id,
        "memory.retain",
        "memory_record",
        result.get("record_id"),
        {"category": payload.category, "source_type": payload.source_type},
        request.client.host if request.client else None,
    )
    db.commit()
    return result


@router.post("/recall")
def recall(
    payload: MemoryRecallRequest,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return memory_service.recall(
            db,
            ctx.organization,
            query=payload.query,
            types=payload.types,
            max_tokens=payload.max_tokens,
            budget=payload.budget,
        )
    except memory_service.HindsightUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/reflect")
def reflect(
    payload: MemoryReflectRequest,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return memory_service.reflect(
            db,
            ctx.organization,
            query=payload.query,
            context=payload.context,
            budget=payload.budget,
        )
    except memory_service.HindsightUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/reset")
def reset(
    confirm: bool = Query(default=False),
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    """Reset the demo organization's memory bank. Refused for non-demo organizations."""
    if not confirm:
        raise HTTPException(status_code=422, detail="Pass confirm=true to reset the bank")
    if not ctx.organization.is_demo:
        raise HTTPException(status_code=403, detail="Memory reset is only available for the demo organization")
    memory_service.reset_bank(db, ctx.organization)
    audit(db, ctx.organization.id, ctx.user.id, "memory.reset", "memory_bank", None, {"demo_only": True})
    db.commit()
    return {"reset": True, "bank_id": ctx.organization.memory_bank_id}
