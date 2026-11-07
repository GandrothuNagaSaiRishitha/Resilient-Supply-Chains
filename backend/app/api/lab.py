"""Memory Learning Lab endpoints.

Each stage is a separate request so the UI can show real progress and so a slow
provider call does not hold one long HTTP request.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import CurrentContext, audit, get_current_context
from ..schemas import LabStageRequest
from ..services import lab
from ..services.agent import AgentUnavailable

router = APIRouter(prefix="/lab", tags=["memory-lab"])


@router.get("/rubric")
def rubric() -> dict:
    return {
        "question": lab.LAB_QUESTION,
        "rubric": lab.RUBRIC,
        "max_score": 100,
        "valid_stages": list(lab.VALID_STAGES),
        "scoring": "Deterministic checks over the answer text; no model judge and no fabricated points.",
    }


@router.get("/experiments")
def experiments(
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    return {"experiments": lab.experiments(db, ctx.organization)}


@router.get("/summary")
def summary(
    experiment_id: str | None = Query(default=None),
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    return lab.experiment_summary(db, ctx.organization, experiment_id)


@router.post("/experiment/new")
def new_experiment(
    request: Request,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    experiment_id = lab.reset_experiment(db, ctx.organization)
    audit(
        db,
        ctx.organization.id,
        ctx.user.id,
        "lab.experiment_new",
        "evaluation_run",
        experiment_id,
        {"bank": lab.memory_service.lab_bank_id(ctx.organization)},
        request.client.host if request.client else None,
    )
    db.commit()
    return {
        "experiment_id": experiment_id,
        "bank_id": lab.memory_service.lab_bank_id(ctx.organization),
        "valid_stages": list(lab.VALID_STAGES),
    }


@router.post("/stage")
def run_stage(
    payload: LabStageRequest,
    request: Request,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    if payload.stage not in lab.VALID_STAGES:
        raise HTTPException(status_code=422, detail=f"stage must be one of {list(lab.VALID_STAGES)}")
    try:
        result = lab.run_stage(
            db,
            ctx.organization,
            ctx.user,
            stage=payload.stage,
            experiment_id=payload.experiment_id,
            force=payload.force,
        )
    except AgentUnavailable as exc:
        raise HTTPException(status_code=503, detail=f"Agent unavailable: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    audit(
        db,
        ctx.organization.id,
        ctx.user.id,
        "lab.stage",
        "evaluation_run",
        result.get("run_id"),
        {
            "stage": payload.stage,
            "experiment_id": result.get("experiment_id"),
            "score": result.get("total_score"),
            "memory_count": result.get("memory_count"),
        },
        request.client.host if request.client else None,
    )
    db.commit()
    return result
