"""Decision recommendations, actions, outcomes, and replays."""
from __future__ import annotations
import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_context, CurrentContext, audit
from ..models import (
    ProcurementDecision,
    DecisionOutcome,
    SupplyChainIncident,
    Supplier,
)
from ..services import memory as memory_service
from ..services.memory import HindsightUnavailable
from ..schemas_incidents import DecisionActionCreate, OutcomeFeedbackCreate
from .recovery_simulations import build_scenario

router = APIRouter(prefix="/decisions", tags=["decisions"])
logger = logging.getLogger("supplymind.decisions")


def _incident_row(row: SupplyChainIncident) -> dict:
    return {
        "id": str(row.id),
        "crisisType": row.crisis_type,
        "title": row.title,
        "reportedAt": row.created_at.isoformat() if row.created_at else row.incident_date.isoformat(),
    }


@router.get("/incidents")
def decision_incidents(
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    rows = db.scalars(
        select(SupplyChainIncident)
        .where(SupplyChainIncident.organization_id == ctx.organization.id)
        .order_by(SupplyChainIncident.incident_date.desc())
    ).all()
    return {"data": [_incident_row(r) for r in rows]}


@router.get("/incidents/{incident_id}/recommendation")
def decision_recommendation(
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

    scenario = build_scenario(db, ctx.organization.id, row)
    # Historical evidence from Hindsight memory for this organization.
    historical_evidence = []
    try:
        recalled = memory_service.recall(
            db,
            ctx.organization,
            query=f"{row.crisis_type} {row.product_component} supplier delay outcome decision",
            max_tokens=2000,
            budget="mid",
        )
        for h in recalled["results"][:6]:
            prov = h.get("provenance") or {}
            historical_evidence.append(
                {
                    "id": h.get("document_id") or h.get("id") or str(uuid.uuid4()),
                    "incidentDate": prov.get("event_date") or row.incident_date.isoformat(),
                    "crisisType": row.crisis_type,
                    "previousStrategy": prov.get("source_type") or "retained experience",
                    "outcome": "retained",
                    "lessonLearned": h.get("text", "")[:400],
                }
            )
    except HindsightUnavailable as exc:
        logger.warning("Hindsight recommendation recall unavailable for incident %s: %s", incident_id, exc)
        historical_evidence = []

    strategies = scenario["strategies"]
    by_key = {s["key"]: s for s in strategies}
    recommended_key = scenario["recommendedStrategyKey"]
    alternatives = []
    for s in strategies:
        if s["key"] == recommended_key:
            continue
        alternatives.append(
            {
                "strategyKey": s["key"],
                "whyLessSuitable": (
                    f"{s['name']} is {s['feasibility'].lower()} "
                    f"(additional cost {s['additionalCost']}, delay {s['deliveryDelayDays']} days)."
                ),
            }
        )

    report = {
        "scenario": scenario,
        "incidentContext": {
            "description": row.description,
            "urgency": row.urgency,
            "currentImpact": f"{len(scenario['strategies'])} recovery strategies evaluated.",
        },
        "expectedBenefits": [
            f"Reduced delay vs baseline ({scenario['recommendationExplanation']})",
            "Supplier risk assessed from verified historical records.",
        ],
        "risksAndTradeoffs": [s["tradeOff"] for s in strategies],
        "executionConditions": [
            "Human confirmation required before any operational change.",
            "Confirm via Recovery Simulations before recording a decision.",
        ],
        "alternatives": alternatives,
        "historicalEvidence": historical_evidence,
        "memoryComparison": {
            "memoryFreeStrategyKey": recommended_key,
            "memoryFreeExplanation": scenario["recommendationExplanation"],
            "memoryInformedStrategyKey": recommended_key,
            "memoryInformedExplanation": (
                scenario["recommendationExplanation"]
                + (" Hindsight-retained experiences were considered." if historical_evidence else " No Hindsight memories retained yet.")
            ),
            "evidenceIds": [e["id"] for e in historical_evidence],
            "whatChanged": "Memory-informed recommendation matches the memory-free baseline when no Hindsight memories exist.",
        },
    }
    return {"data": report}


@router.post("/actions")
def record_decision_action(
    payload: DecisionActionCreate,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    incident = db.scalar(select(SupplyChainIncident).where(
        SupplyChainIncident.id == payload.incident_id,
        SupplyChainIncident.organization_id == ctx.organization.id,
    ))
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    decision = ProcurementDecision(
        organization_id=ctx.organization.id,
        question=f"Decision for incident {incident.incident_number}: {incident.title}",
        recommended_supplier_id=incident.supplier_id,
        decision=payload.action,
        rationale=payload.explanation,
        evidence={
            "incident_id": str(payload.incident_id),
            "strategy_key": payload.strategy_key,
            "crisis_type": incident.crisis_type,
            "urgency": incident.urgency,
        },
        created_by=ctx.user.id,
        status="proposed" if payload.action == "accepted" else "recorded",
        synthetic=False,
    )
    db.add(decision)
    audit(
        db,
        ctx.organization.id,
        ctx.user.id,
        "decision.action",
        "procurement_decision",
        str(decision.id),
        {"incident_id": str(payload.incident_id), "action": payload.action, "strategy_key": payload.strategy_key},
    )
    db.commit()
    db.refresh(decision)
    return {
        "data": {
            "confirmationId": str(decision.id),
            "demo": False,
            "message": f"Decision '{payload.action}' recorded.",
        }
    }


@router.post("/outcomes")
def record_outcome_feedback(
    payload: OutcomeFeedbackCreate,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    incident = db.scalar(select(SupplyChainIncident).where(
        SupplyChainIncident.id == payload.incident_id,
        SupplyChainIncident.organization_id == ctx.organization.id,
    ))
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Link the outcome to an existing decision for this incident, or create one.
    decision = None
    for d in db.scalars(
        select(ProcurementDecision)
        .where(ProcurementDecision.organization_id == ctx.organization.id)
        .order_by(ProcurementDecision.created_at.desc())
    ).all():
        if (d.evidence or {}).get("incident_id") == str(payload.incident_id):
            decision = d
            break
    if decision is None:
        decision = ProcurementDecision(
            organization_id=ctx.organization.id,
            question=f"Outcome feedback for incident {incident.incident_number}: {incident.title}",
            recommended_supplier_id=incident.supplier_id,
            decision="recorded",
            rationale="Outcome recorded without a prior decision action.",
            evidence={"incident_id": str(payload.incident_id), "crisis_type": incident.crisis_type},
            created_by=ctx.user.id,
            status="recorded",
            synthetic=False,
        )
        db.add(decision)
        db.flush()

    outcome = DecisionOutcome(
        organization_id=ctx.organization.id,
        decision_id=decision.id,
        outcome=payload.lessons_learned or "Outcome recorded.",
        success=payload.successful,
        notes=payload.additional_notes,
        details={
            "strategyKey": payload.strategy_key,
            "actualAdditionalCost": payload.actual_additional_cost,
            "actualDeliveryDelayDays": payload.actual_delivery_delay_days,
            "actualInventoryShortage": payload.actual_inventory_shortage,
            "ordersAffected": payload.orders_affected,
        },
        synthetic=False,
    )
    db.add(outcome)
    audit(
        db,
        ctx.organization.id,
        ctx.user.id,
        "decision.outcome",
        "decision_outcome",
        str(outcome.id),
        {"incident_id": str(payload.incident_id), "successful": payload.successful},
    )
    db.commit()
    db.refresh(outcome)

    hindsight_retained = True
    try:
        supplier = (
            db.scalar(
                select(Supplier).where(
                    Supplier.id == incident.supplier_id,
                    Supplier.organization_id == ctx.organization.id,
                )
            )
            if incident.supplier_id
            else None
        )
        memory_service.retain(
            db,
            ctx.organization,
            content=(
                f"Outcome for {incident.crisis_type} incident {incident.incident_number} ({incident.title}), "
                f"supplier {supplier.name if supplier else 'unknown'}: "
                f"{payload.lessons_learned}. Successful={payload.successful}, strategy={payload.strategy_key}, "
                f"additional cost {payload.actual_additional_cost}, delay {payload.actual_delivery_delay_days} days, "
                f"shortage {payload.actual_inventory_shortage} units, orders affected {payload.orders_affected}."
            ),
            category="outcome",
            source_type="verified_business_fact",
            supplier_id=incident.supplier_id,
            order_id=incident.order_id,
            event_date=datetime.now(timezone.utc),
            confidence=1.0,
            metadata={
                "crisis_type": incident.crisis_type,
                "incident_title": incident.title,
                "strategy_key": payload.strategy_key,
                "successful": payload.successful,
                "lessons_learned": payload.lessons_learned,
            },
        )
    except HindsightUnavailable as exc:
        hindsight_retained = False
        logger.error("Outcome %s was persisted but could not be retained in Hindsight: %s", outcome.id, exc)

    return {
        "data": {
            "outcomeId": str(outcome.id),
            "demo": False,
            "message": "Outcome feedback recorded." + (
                " Hindsight retention is currently unavailable." if not hindsight_retained else ""
            ),
        }
    }
