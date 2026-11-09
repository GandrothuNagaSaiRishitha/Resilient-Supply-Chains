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
from ..services.agent import AgentService, AgentUnavailable
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


def _historical_evidence(hits: list[dict], incident: SupplyChainIncident) -> list[dict]:
    evidence = []
    for hit in hits[:6]:
        provenance = hit.get("provenance") or {}
        metadata = hit.get("metadata") or {}
        evidence_id = hit.get("document_id") or hit.get("id")
        if not evidence_id:
            continue
        successful = provenance.get("successful", metadata.get("successful"))
        if successful is True or str(successful).lower() == "true":
            outcome = "Successful"
        elif successful is False or str(successful).lower() == "false":
            outcome = "Unsuccessful"
        else:
            outcome = "Outcome not recorded"
        evidence.append(
            {
                "id": str(evidence_id),
                "incidentDate": provenance.get("event_date") or hit.get("occurred_start") or "Date not recorded",
                "crisisType": provenance.get("crisis_type") or metadata.get("crisis_type") or "Historical experience",
                "previousStrategy": provenance.get("strategy_key") or metadata.get("strategy_key") or "Strategy not recorded",
                "outcome": outcome,
                "lessonLearned": (
                    provenance.get("lessons_learned")
                    or hit.get("text", "")[:600]
                    or "No lesson text was returned."
                ),
                "verified": provenance.get("verified", metadata.get("verified")),
            }
        )
    return evidence


def _evidence_strength(evidence: list[dict]) -> str:
    verified_count = sum(item.get("verified") is True for item in evidence)
    if not evidence:
        return "none"
    if verified_count >= 3:
        return "strong"
    if verified_count:
        return "moderate"
    return "limited"


def _fallback_recommendation(scenario: dict, evidence: list[dict]) -> dict:
    strategy = next(
        item for item in scenario["strategies"] if item["key"] == scenario["recommendedStrategyKey"]
    )
    return {
        "status": "fallback",
        "strategyKey": strategy["key"],
        "rationale": scenario["recommendationExplanation"],
        "estimatedImpact": (
            f"Baseline estimate: additional cost {strategy['additionalCost']}, "
            f"delivery delay {strategy['deliveryDelayDays']} days, "
            f"projected shortage {strategy['projectedShortageUnits']} units."
        ),
        "risks": [strategy["feasibilityNote"]],
        "tradeOffs": [strategy["tradeOff"]],
        "evidenceStrength": _evidence_strength(evidence),
        "evidenceIds": [],
        "notice": "AI recommendation unavailable; showing the deterministic recovery baseline.",
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
    supplier = (
        db.scalar(
            select(Supplier).where(
                Supplier.id == row.supplier_id,
                Supplier.organization_id == ctx.organization.id,
            )
        )
        if row.supplier_id
        else None
    )
    incident_context = {
        "id": str(row.id),
        "incidentNumber": row.incident_number,
        "crisisType": row.crisis_type,
        "title": row.title,
        "description": row.description,
        "supplier": supplier.name if supplier else "Unassigned",
        "productComponent": row.product_component,
        "origin": row.origin,
        "destination": row.destination,
        "expectedDelayDays": row.expected_delay_days,
        "availableInventoryQuantity": row.available_inventory_quantity,
        "affectedOrders": row.affected_orders,
        "urgency": row.urgency,
        "incidentDate": row.incident_date.isoformat(),
        "scenarioImpact": scenario["summary"],
    }
    query = " ".join(
        str(value)
        for value in (
            row.crisis_type,
            row.title,
            row.description,
            supplier.name if supplier else None,
            row.product_component,
            row.origin,
            row.destination,
            f"expected delay {row.expected_delay_days} days" if row.expected_delay_days is not None else None,
            f"available inventory {row.available_inventory_quantity}" if row.available_inventory_quantity is not None else None,
            f"affected orders {row.affected_orders}" if row.affected_orders is not None else None,
            row.urgency,
        )
        if value is not None and str(value).strip()
    )
    hits: list[dict] = []
    memory_status = "empty"
    try:
        recalled = memory_service.recall(
            db,
            ctx.organization,
            query=query,
            max_tokens=3500,
            budget="mid",
        )
        hits = recalled["results"][:6]
        memory_status = "available" if hits else "empty"
    except HindsightUnavailable as exc:
        logger.warning("Hindsight recommendation recall unavailable for incident %s: %s", incident_id, exc)
        memory_status = "unavailable"

    historical_evidence = _historical_evidence(hits, row)
    reflection = None
    reflection_status = "not_needed"
    if hits:
        try:
            reflected = memory_service.reflect(
                db,
                ctx.organization,
                query=query,
                context="Synthesize evidence for this recovery recommendation. Distinguish observed outcomes from inference.",
                budget="mid",
            )
            reflection = reflected.get("text")
            reflection_status = "used" if reflection else "empty"
        except HindsightUnavailable as exc:
            logger.warning("Hindsight recommendation reflect unavailable for incident %s: %s", incident_id, exc)
            reflection_status = "unavailable"

    try:
        generated = AgentService(db, ctx.organization, ctx.user).generate_decision_recommendation(
            incident=incident_context,
            scenario=scenario,
            historical_evidence=historical_evidence,
            reflection=reflection,
        )
        evidence_ids = generated["evidence_ids"]
        ai_recommendation = {
            "status": "generated",
            "strategyKey": generated["strategy_key"],
            "rationale": generated["rationale"],
            "estimatedImpact": generated["estimated_impact"],
            "risks": generated["risks"],
            "tradeOffs": generated["trade_offs"],
            "evidenceStrength": _evidence_strength(historical_evidence),
            "evidenceIds": evidence_ids,
            "notice": None,
        }
    except AgentUnavailable as exc:
        logger.warning("Groq recommendation unavailable for incident %s (%s)", incident_id, type(exc).__name__)
        ai_recommendation = _fallback_recommendation(scenario, historical_evidence)

    strategies = scenario["strategies"]
    recommended_key = ai_recommendation["strategyKey"]
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
        "expectedBenefits": [ai_recommendation["estimatedImpact"]],
        "risksAndTradeoffs": ai_recommendation["risks"] + ai_recommendation["tradeOffs"],
        "executionConditions": [
            "Human confirmation required before any operational change.",
            "Confirm via Recovery Simulations before recording a decision.",
        ],
        "alternatives": alternatives,
        "historicalEvidence": historical_evidence,
        "aiRecommendation": ai_recommendation,
        "memoryStatus": memory_status,
        "reflectionStatus": reflection_status,
        "memoryComparison": {
            "memoryFreeStrategyKey": scenario["recommendedStrategyKey"],
            "memoryFreeExplanation": scenario["recommendationExplanation"],
            "memoryInformedStrategyKey": recommended_key,
            "memoryInformedExplanation": ai_recommendation["rationale"],
            "evidenceIds": ai_recommendation["evidenceIds"],
            "whatChanged": (
                "Groq generated this suggestion using current incident data and retrieved evidence."
                if ai_recommendation["status"] == "generated"
                else "The deterministic scenario baseline is shown because Groq did not return a valid recommendation."
            ),
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
                f"supplier {supplier.name if supplier else 'unknown'}, component {incident.product_component}, "
                f"urgency {incident.urgency}, operational context: {incident.description}. "
                f"Route {incident.origin or 'not recorded'} to {incident.destination or 'not recorded'}: "
                f"{payload.lessons_learned}. Successful={payload.successful}, strategy={payload.strategy_key}, "
                f"additional cost {payload.actual_additional_cost}, delay {payload.actual_delivery_delay_days} days, "
                f"shortage {payload.actual_inventory_shortage} units, orders affected {payload.orders_affected}."
            ),
            category="outcome",
            source_type="user_reported_fact",
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
                "product_component": incident.product_component,
                "urgency": incident.urgency,
                "expected_delay_days": incident.expected_delay_days,
                "origin": incident.origin,
                "destination": incident.destination,
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
