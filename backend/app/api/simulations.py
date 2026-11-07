"""What-if disruption simulations and supplier comparison."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import CurrentContext, get_current_context
from ..models import Supplier
from ..schemas import WhatIfRequest
from ..services import memory as memory_service
from ..services.tools import ToolContext, ToolError, evaluate_contingency_options, compare_suppliers

router = APIRouter(tags=["simulations"])


@router.post("/what-if")
def what_if(
    payload: WhatIfRequest,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    supplier = db.get(Supplier, payload.supplier_id)
    if supplier is None or supplier.organization_id != ctx.organization.id:
        raise HTTPException(status_code=404, detail="Supplier not found")
    tool_ctx = ToolContext(db=db, organization=ctx.organization, user=ctx.user)
    try:
        result = evaluate_contingency_options(
            tool_ctx, supplier=supplier.name, disruption_days=payload.disruption_days
        )
    except ToolError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    memory_context = []
    try:
        recalled = memory_service.recall(
            db,
            ctx.organization,
            query=f"{supplier.name} delivery delays quality issues and past decisions",
            max_tokens=1800,
            budget="mid",
        )
        memory_context = [
            {"text": h["text"][:500], "type": h.get("type"), "score": h.get("score")}
            for h in recalled["results"][:5]
        ]
    except Exception:  # noqa: BLE001
        memory_context = []

    result["question"] = payload.question
    result["memory_context"] = memory_context
    result["disclaimer"] = (
        "This is a deterministic simulation over historical records, not a delivery forecast. "
        "Historical performance is a risk indicator, never a guarantee."
    )
    return result


@router.post("/suppliers/compare")
def compare(
    suppliers: list[str],
    requirements: str | None = None,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    tool_ctx = ToolContext(db=db, organization=ctx.organization, user=ctx.user)
    try:
        result = compare_suppliers(tool_ctx, suppliers=suppliers, requirements=requirements)
    except ToolError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result
