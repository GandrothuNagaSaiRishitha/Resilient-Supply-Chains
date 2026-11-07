"""AI procurement assistant endpoints (Groq tool calling + Hindsight memory)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import CurrentContext, audit, get_current_context
from ..models import AgentRun, Conversation, Message
from ..schemas import ChatRequest
from ..services.agent import AgentService, AgentUnavailable
from ..services.tools import ToolError

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat")
def chat(
    payload: ChatRequest,
    request: Request,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    service = AgentService(db, ctx.organization, ctx.user)
    try:
        return service.run(
            message=payload.message,
            conversation_id=payload.conversation_id,
            memory_enabled=payload.memory_enabled,
            new_conversation=payload.new_conversation,
        )
    except ToolError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except AgentUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/runs")
def list_runs(
    limit: int = Query(default=50, ge=1, le=200),
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    runs = db.scalars(
        select(AgentRun)
        .where(AgentRun.organization_id == ctx.organization.id)
        .order_by(AgentRun.created_at.desc())
        .limit(limit)
    ).all()
    return {
        "count": len(runs),
        "runs": [
            {
                "id": str(r.id),
                "conversation_id": str(r.conversation_id) if r.conversation_id else None,
                "agent": r.agent,
                "question": r.question,
                "answer": r.answer,
                "status": r.status,
                "memory_enabled": r.memory_enabled,
                "model": r.model,
                "duration_ms": r.duration_ms,
                "tool_call_count": len(r.tool_calls or []),
                "memory_hit_count": len((r.evidence or {}).get("memory_hits", [])),
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in runs
        ],
    }


@router.get("/runs/{run_id}")
def get_run(
    run_id: uuid.UUID,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    run = db.get(AgentRun, run_id)
    if run is None or run.organization_id != ctx.organization.id:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return {
        "id": str(run.id),
        "conversation_id": str(run.conversation_id) if run.conversation_id else None,
        "question": run.question,
        "answer": run.answer,
        "status": run.status,
        "memory_enabled": run.memory_enabled,
        "tool_calls": run.tool_calls,
        "evidence": run.evidence,
        "model": run.model,
        "duration_ms": run.duration_ms,
        "error": run.error,
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }


@router.get("/conversations")
def list_conversations(
    limit: int = Query(default=30, ge=1, le=100),
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    rows = db.scalars(
        select(Conversation)
        .where(Conversation.organization_id == ctx.organization.id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    ).all()
    return {
        "count": len(rows),
        "conversations": [
            {
                "id": str(c.id),
                "title": c.title,
                "memory_enabled": c.memory_enabled,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in rows
        ],
    }


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: uuid.UUID,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    conv = db.get(Conversation, conversation_id)
    if conv is None or conv.organization_id != ctx.organization.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = db.scalars(
        select(Message)
        .where(Message.conversation_id == conv.id, Message.organization_id == ctx.organization.id)
        .order_by(Message.created_at)
    ).all()
    return {
        "id": str(conv.id),
        "title": conv.title,
        "memory_enabled": conv.memory_enabled,
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    }
