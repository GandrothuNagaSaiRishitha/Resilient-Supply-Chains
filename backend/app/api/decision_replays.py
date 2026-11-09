"""Decision replay: historical reconstruction and memory-informed comparison."""
from __future__ import annotations
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_context, CurrentContext, audit
from ..models import (
    ProcurementDecision,
    DecisionOutcome,
    SupplyChainIncident,
)
from ..services import memory as memory_service
from .recovery_simulations import build_scenario

router = APIRouter(prefix="/decision-replays", tags=["decision-replays"])
logger = logging.getLogger("supplymind.decision_replays")


@router.get("/incidents")
def replay_incidents(
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    rows = db.scalars(
        select(SupplyChainIncident)
        .where(SupplyChainIncident.organization_id == ctx.organization.id)
        .order_by(SupplyChainIncident.incident_date.desc())
    ).all()
    return {
        "data": [
            {
                "id": str(r.id),
                "crisisType": r.crisis_type,
                "title": r.title,
                "reportedAt": r.created_at.isoformat() if r.created_at else r.incident_date.isoformat(),
            }
            for r in rows
        ],
    }


@router.get("/{incident_id}")
def replay_record(
    incident_id: uuid.UUID,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    row = db.scalar(
        select(SupplyChainIncident).where(
            SupplyChainIncident.id == incident_id,
            SupplyChainIncident.organization_id == ctx.organization.id,
        )
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    decisions = db.scalars(
        select(ProcurementDecision)
        .where(ProcurementDecision.organization_id == ctx.organization.id)
        .order_by(ProcurementDecision.created_at.desc())
    ).all()
    decision = next(
        (d for d in decisions if (d.evidence or {}).get("incident_id") == str(incident_id)),
        None,
    )
    outcome = (
        db.scalar(
            select(DecisionOutcome).where(
                DecisionOutcome.organization_id == ctx.organization.id,
                DecisionOutcome.decision_id == decision.id,
            ).order_by(DecisionOutcome.recorded_at.desc())
        )
        if decision
        else None
    )

    scenario = build_scenario(db, ctx.organization.id, row)
    strategy_keys = {item["key"] for item in scenario["strategies"]}
    details = outcome.details if outcome else {}
    original_key = (
        (decision.evidence or {}).get("strategy_key") if decision else None
    ) or details.get("strategyKey")
    if original_key not in strategy_keys:
        original_key = scenario["recommendedStrategyKey"]
    evidence = []
    memory_informed_key = None
    memory_status = "unavailable"
    try:
        recalled = memory_service.recall(
            db,
            ctx.organization,
            query=f"{row.crisis_type} {row.product_component} supplier recovery decision outcome",
            max_tokens=2000,
            budget="mid",
        )
        memory_status = "available" if recalled["results"] else "empty"
        for hit in recalled["results"][:6]:
            provenance = hit.get("provenance") or {}
            strategy = provenance.get("strategy_key")
            if strategy in strategy_keys and memory_informed_key is None:
                memory_informed_key = strategy
            evidence.append({
                "id": hit.get("document_id") or hit.get("id") or str(uuid.uuid4()),
                "incidentDate": provenance.get("event_date") or row.incident_date.date().isoformat(),
                "crisisType": provenance.get("crisis_type") or "Retained experience",
                "decision": strategy or "Retained supply-chain experience",
                "actualOutcome": hit.get("text", ""),
                "lesson": provenance.get("lessons_learned") or hit.get("text", ""),
            })
    except memory_service.HindsightUnavailable as exc:
        logger.warning("Hindsight replay recall unavailable for incident %s: %s", incident_id, exc)
    if memory_status == "unavailable":
        evidence_explanation = "Hindsight is unavailable; historical evidence could not be retrieved."
        comparison_explanation = "No memory-informed comparison is available because Hindsight could not be reached."
    elif memory_status == "empty":
        evidence_explanation = "Hindsight returned no relevant memories for this incident."
        comparison_explanation = "No memory-informed comparison is available because Hindsight returned no relevant memories."
    elif memory_informed_key is None:
        evidence_explanation = f"{len(evidence)} Hindsight memories were retrieved, but none identified a comparable recovery strategy."
        comparison_explanation = "Historical memories were retrieved, but none contained a comparable recovery strategy."
    else:
        evidence_explanation = f"{len(evidence)} Hindsight memories were retrieved for this organization."
        comparison_explanation = (
            "Hindsight evidence changed the strategy used for comparison."
            if memory_informed_key != scenario["recommendedStrategyKey"] else
            "The memory-informed strategy matches the baseline recommendation."
        )
    return {
        "data": {
            "incident": {
                "id": str(row.id),
                "crisisType": row.crisis_type,
                "title": row.title,
                "reportedAt": row.created_at.isoformat() if row.created_at else row.incident_date.isoformat(),
            },
            "originalStrategyKey": original_key,
            "originalDecision": decision.decision if decision else None,
            "originalRationale": decision.rationale if decision else None,
            "actualOutcome": {
                "additionalCost": details.get("actualAdditionalCost", 0),
                "deliveryDelayDays": details.get("actualDeliveryDelayDays", 0),
                "inventoryShortageUnits": details.get("actualInventoryShortage", 0),
                "ordersAffected": details.get("ordersAffected", row.affected_orders),
                "successful": outcome.success if outcome else False,
                "summary": outcome.outcome if outcome else "No outcome feedback has been recorded for this incident.",
            },
            "memoryFreeStrategyKey": scenario["recommendedStrategyKey"],
            "memoryInformedStrategyKey": memory_informed_key,
            "memoryStatus": memory_status,
            "historicalEvidence": evidence,
            "evidenceExplanation": evidence_explanation,
            "comparisonExplanation": comparison_explanation,
            "scenario": scenario,
        }
    }


@router.post("/{incident_id}/run")
def run_replay(
    incident_id: uuid.UUID,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    row = db.scalar(
        select(SupplyChainIncident).where(
            SupplyChainIncident.id == incident_id,
            SupplyChainIncident.organization_id == ctx.organization.id,
        )
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Memory-informed strategy from organization-scoped Hindsight recall.
    memory_informed_key = None
    memory_informed_explanation = ""
    memory_status = "unavailable"
    try:
        recalled = memory_service.recall(
            db,
            ctx.organization,
            query=f"{row.crisis_type} {row.product_component} supplier recovery decision outcome",
            max_tokens=2000,
            budget="mid",
        )
        memory_status = "available" if recalled["results"] else "empty"
        if recalled["results"]:
            evidence = recalled["results"][0]
            memory_informed_key = (evidence.get("provenance") or {}).get("strategy_key")
            if memory_informed_key not in {s["key"] for s in build_scenario(db, ctx.organization.id, row)["strategies"]}:
                memory_informed_key = None
            memory_informed_explanation = (
                f"Hindsight returned {len(recalled['results'])} retained experiences for comparison."
                if memory_informed_key is not None else
                f"Hindsight returned {len(recalled['results'])} retained experiences, but none identified a comparable recovery strategy."
            )
    except memory_service.HindsightUnavailable as exc:
        logger.warning("Hindsight replay recall unavailable for incident %s: %s", incident_id, exc)

    scenario = build_scenario(db, ctx.organization.id, row)
    memory_free_key = scenario["recommendedStrategyKey"]

    audit(
        db,
        ctx.organization.id,
        ctx.user.id,
        "replay.run",
        "decision_replay",
        str(incident_id),
        {
            "memory_free_key": memory_free_key,
            "memory_informed_key": memory_informed_key,
            "memory_status": memory_status,
        },
    )
    db.commit()

    return {
        "data": {
            "incidentId": str(incident_id),
            "replayed": True,
            "memoryStatus": memory_status,
            "message": (
                memory_informed_explanation
                or (
                    "Replay baseline completed; Hindsight is unavailable, so no memory-informed comparison was performed."
                    if memory_status == "unavailable" else
                    "Replay baseline completed; Hindsight returned no relevant memories, so no memory-informed comparison was performed."
                )
            ) + " The original decision is unchanged.",
        }
    }
