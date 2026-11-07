"""Memory Learning Lab.

This module runs a reproducible before/after evaluation of Hindsight memory.
It never invents scores:

* The same question and the same organization dataset are used at every stage.
* Stage 0 is a real agent run with memory disabled. That single baseline result
  is stored once and reused for every later comparison.
* Stages 1/5/10/20 retain the first N curated organizational experiences in an
  isolated Hindsight bank (``<org bank>__lab``) and then run the same agent.
* Answers are scored by a deterministic rubric that inspects the answer text.
  The rubric, its checks and the answers themselves are persisted so anyone can
  audit the score.

The lab bank is derived on the server and is never accepted from a client.
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..models import EvaluationResult, EvaluationRun, Organization, User
from . import memory as memory_service
from .agent import AgentService, AgentUnavailable
from .seed import LAB_EXPERIENCES

logger = logging.getLogger("supplymind.lab")

VALID_STAGES = (0, 1, 5, 10, 20)

LAB_QUESTION = (
    "For our urgent 1,000-unit MCU-1000 microcontroller order, which supplier should we "
    "choose and why? Compare Alpha Components and Meridian Electronics. Use our historical "
    "delivery, quality and communication records, our past procurement decision outcomes, "
    "and our company procurement preference. Give a clear recommendation and the risks."
)

# Deterministic, auditable rubric. Each dimension is worth a fixed number of
# points. A check only passes when the answer text itself contains the evidence.
RUBRIC: list[dict[str, Any]] = [
    {
        "dimension": "supplier_recommendation",
        "weight": 20,
        "description": "Recommends Meridian Electronics (not Alpha) for the urgent order.",
    },
    {
        "dimension": "delay_evidence",
        "weight": 15,
        "description": "Cites Alpha's concrete delivery slippage (roughly 10 days late / 15 days actual).",
    },
    {
        "dimension": "quality_evidence",
        "weight": 15,
        "description": "Cites Alpha's concrete quality problem (solder defects, ~8% rejection).",
    },
    {
        "dimension": "communication_evidence",
        "weight": 15,
        "description": "Cites Alpha's communication failures (12 days without status, missed flights).",
    },
    {
        "dimension": "decision_outcome_evidence",
        "weight": 20,
        "description": "Cites the outcome of the previous price-first Alpha decision (10-day late delivery, overtime / three shifts).",
    },
    {
        "dimension": "policy_preference",
        "weight": 15,
        "description": "Applies the company preference: on-time verified record over lowest price, with a delivery buffer.",
    },
]


def _has(text: str, pattern: str) -> bool:
    return re.search(pattern, text, re.IGNORECASE) is not None


def score_answer(answer: str, memory_hits: list[dict] | None = None) -> list[dict]:
    """Score an answer against the fixed rubric.

    This is deterministic: identical text always receives the identical score.
    Memory hit count is recorded for context but never adds points.
    """
    text = (answer or "").lower()
    results: list[dict] = []

    def add(dimension: str, weight: int, score: float, explanation: str) -> None:
        results.append(
            {
                "dimension": dimension,
                "weight": weight,
                "score": round(float(score), 2),
                "explanation": explanation,
            }
        )

    # 1. Supplier recommendation.
    recommends_meridian = _has(
        text,
        r"\b(choose|select|recommend|use|switch to|go with|award)\b[^.\n]{0,80}\bmeridian\b"
        r"|\bmeridian\b[^.\n]{0,80}\b(recommended|recommendation|best|preferred|should)\b",
    )
    mentions_meridian = _has(text, r"\bmeridian\b")
    recommends_alpha = _has(
        text,
        r"\b(choose|select|recommend|use|go with)\b[^.\n]{0,80}\balpha\b",
    ) and not _has(text, r"\b(do not|don't|avoid|not)\s+(choose|select|recommend|use)\b[^.\n]{0,40}\balpha\b")
    if recommends_meridian and not recommends_alpha:
        add("supplier_recommendation", 20, 20, "Explicitly recommends Meridian Electronics.")
    elif recommends_alpha:
        add("supplier_recommendation", 20, 0, "Recommends Alpha Components despite the risk record.")
    elif mentions_meridian:
        add("supplier_recommendation", 20, 10, "Mentions Meridian but does not clearly recommend it.")
    else:
        add("supplier_recommendation", 20, 0, "No clear supplier recommendation found.")

    # 2. Delay evidence: Alpha delivered late. Accept 10-day delay or 15-day delivery.
    delay_hit = _has(
        text,
        r"\balpha\b[^.\n]{0,120}\b(10|ten)\b[\s-]*(day|days)\b"
        r"|\b(10|ten)\b[\s-]*(day|days)\b[^.\n]{0,120}\balpha\b"
        r"|\balpha\b[^.\n]{0,120}\b(15|fifteen)\b[\s-]*(day|days)\b"
        r"|\bdelivered\b[^.\n]{0,60}\b(10|15)\b[\s-]*(day|days)\b[^.\n]{0,60}\blate\b",
    )
    add(
        "delay_evidence",
        15,
        15 if delay_hit else 0,
        "Cites Alpha's concrete delivery slippage." if delay_hit else "No concrete Alpha delay evidence found.",
    )

    # 3. Quality evidence.
    quality_hit = _has(text, r"\bsolder\b|\bdefect(s)?\b|\b8\s?%\b|\brejection\b|\bquality\b[^.\n]{0,40}\balpha\b")
    add(
        "quality_evidence",
        15,
        15 if quality_hit else 0,
        "Cites Alpha's quality defect evidence." if quality_hit else "No concrete Alpha quality evidence found.",
    )

    # 4. Communication evidence.
    communication_hit = _has(
        text,
        r"\b12\b[\s-]*(day|days)\b|\btwelve\b[\s-]*(day|days)\b"
        r"|\bno status update(s)?\b|\bwithout (a )?status\b"
        r"|\bmissed\b[^.\n]{0,40}\bflight(s)?\b|\bcommunication\b[^.\n]{0,40}\balpha\b",
    )
    add(
        "communication_evidence",
        15,
        15 if communication_hit else 0,
        "Cites Alpha's communication failures." if communication_hit else "No concrete communication evidence found.",
    )

    # 5. Previous decision outcome: price-first Alpha decision caused overtime.
    #    Full credit requires the operational outcome, half credit for only the
    #    fact that a previous price-first decision was made.
    outcome_hit = _has(
        text,
        r"\bovertime\b|\bthree shifts\b|\b3 shifts\b|\bdelivered\b[^.\n]{0,60}\b10\b[\s-]*(day|days)\b[^.\n]{0,40}\blate\b",
    )
    prior_decision = _has(
        text,
        r"\bprevious (procurement )?decision\b|\bprice[- ]first\b|\blowest (unit )?price\b|\bcheaper\b|\bcost saving\b",
    )
    if outcome_hit:
        add("decision_outcome_evidence", 20, 20, "Cites the operational outcome of the earlier price-first choice.")
    elif prior_decision:
        add("decision_outcome_evidence", 20, 10, "Mentions the earlier price-first decision but not its outcome.")
    else:
        add("decision_outcome_evidence", 20, 0, "No earlier decision outcome cited.")

    # 6. Company preference.
    preference_hit = _has(
        text,
        r"\b3[\s-]*day (delivery )?buffer\b|\bthree[\s-]*day (delivery )?buffer\b"
        r"|\b(delivery )?buffer\b|\bon[- ]time record\b"
        r"|\breliability\b[^.\n]{0,60}\b(price|cost)\b"
        r"|\bnot\b[^.\n]{0,40}\blowest price\b|\bverified record\b",
    )
    add(
        "policy_preference",
        15,
        15 if preference_hit else 0,
        "Applies the verified-record-over-price / buffer preference."
        if preference_hit
        else "Company procurement preference not applied.",
    )

    return results


def _sum(results: list[dict]) -> float:
    return round(sum(float(r["score"]) for r in results), 2)


def _new_experiment_id() -> str:
    return uuid.uuid4().hex


def reset_experiment(db: Session, organization: Organization) -> str:
    """Start a fresh experiment: clear lab runs and the isolated lab memory bank."""
    for row in db.scalars(
        select(EvaluationResult).where(EvaluationResult.organization_id == organization.id)
    ).all():
        db.delete(row)
    for row in db.scalars(
        select(EvaluationRun).where(EvaluationRun.organization_id == organization.id)
    ).all():
        db.delete(row)
    db.commit()
    memory_service.reset_bank(db, organization, bank_id=memory_service.lab_bank_id(organization))
    experiment_id = _new_experiment_id()
    logger.info("lab experiment %s started for org %s", experiment_id, organization.id)
    return experiment_id


def _prepare_lab_bank(db: Session, organization: Organization, count: int) -> int:
    """Reset the lab bank and retain exactly the first ``count`` experiences."""
    bank = memory_service.lab_bank_id(organization)
    memory_service.reset_bank(db, organization, bank_id=bank)
    retained = 0
    for order_number, supplier_key, category, content, days in LAB_EXPERIENCES[:count]:
        try:
            memory_service.retain(
                db,
                organization,
                content=content,
                category=category,
                source_type="verified_business_fact" if category != "preference" else "user_reported_fact",
                event_date=datetime.now(timezone.utc),
                context=f"{category} supply-chain experience",
                synthetic=True,
                bank_id=bank,
                record_provenance=False,
            )
            retained += 1
        except Exception as exc:  # noqa: BLE001
            logger.warning("lab retain failed at index %s: %s", retained, exc)
            raise
    return retained


def _serialize_run(run: EvaluationRun, results: list[EvaluationResult]) -> dict:
    details = run.details or {}
    return {
        "run_id": str(run.id),
        "experiment_id": details.get("experiment_id"),
        "stage": run.stage,
        "question": run.question,
        "memory_enabled": run.memory_enabled,
        "memory_count": run.memory_count,
        "total_score": run.total_score,
        "max_score": 100,
        "dimensions": [
            {
                "dimension": r.dimension,
                "score": r.score,
                "explanation": r.explanation,
            }
            for r in results
        ],
        "answer": details.get("answer"),
        "memory_hits": details.get("memory_hits", []),
        "reflect_answer": details.get("reflect_answer"),
        "tool_calls": details.get("tool_calls", []),
        "model": details.get("model"),
        "duration_ms": details.get("duration_ms"),
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "reused_baseline": bool(details.get("reused_baseline")),
    }


def _results_for(db: Session, run: EvaluationRun) -> list[EvaluationResult]:
    return list(
        db.scalars(
            select(EvaluationResult)
            .where(EvaluationResult.run_id == run.id)
            .order_by(EvaluationResult.created_at)
        ).all()
    )


def _find_run(db: Session, organization: Organization, experiment_id: str, stage: int) -> EvaluationRun | None:
    runs = db.scalars(
        select(EvaluationRun)
        .where(EvaluationRun.organization_id == organization.id, EvaluationRun.stage == stage)
        .order_by(EvaluationRun.created_at.desc())
    ).all()
    for run in runs:
        if (run.details or {}).get("experiment_id") == experiment_id:
            return run
    return None


def run_stage(
    db: Session,
    organization: Organization,
    user: User | None,
    *,
    stage: int,
    experiment_id: str | None = None,
    force: bool = False,
) -> dict:
    """Run one lab stage. Stage 0 is computed once and reused for comparisons."""
    if stage not in VALID_STAGES:
        raise ValueError(f"stage must be one of {VALID_STAGES}")
    experiment_id = experiment_id or _new_experiment_id()

    if not force:
        existing = _find_run(db, organization, experiment_id, stage)
        if existing is not None:
            payload = _serialize_run(existing, _results_for(db, existing))
            payload["reused"] = True
            return payload

    bank = memory_service.lab_bank_id(organization)
    memory_count = 0
    if stage > 0:
        memory_count = _prepare_lab_bank(db, organization, stage)

    last_error: Exception | None = None
    for attempt in range(2):
        try:
            agent = AgentService(db, organization, user, memory_bank_id=bank)
            result = agent.run(
                message=LAB_QUESTION,
                memory_enabled=stage > 0,
                new_conversation=True,
            )
            break
        except AgentUnavailable as exc:
            # A transient provider failure should not be recorded as a score.
            last_error = exc
            logger.warning("lab stage %s attempt %s failed: %s", stage, attempt + 1, exc)
            if attempt == 1:
                raise
    else:  # pragma: no cover - defensive
        raise RuntimeError(f"lab stage failed: {last_error}")

    answer = result["answer"]
    hits = result.get("memory_hits") or []
    dimensions = score_answer(answer, hits)
    total = _sum(dimensions)

    run = EvaluationRun(
        organization_id=organization.id,
        stage=stage,
        question=LAB_QUESTION,
        memory_enabled=stage > 0,
        total_score=total,
        memory_count=memory_count,
        details={
            "experiment_id": experiment_id,
            "answer": answer,
            "memory_hits": [
                {
                    "text": h.get("text", "")[:700],
                    "type": h.get("type"),
                    "score": h.get("score"),
                    "document_id": h.get("document_id"),
                }
                for h in hits[:12]
            ],
            "reflect_answer": result.get("reflect_answer"),
            "tool_calls": result.get("tool_calls", []),
            "model": result.get("model"),
            "duration_ms": result.get("duration_ms"),
            "rubric": RUBRIC,
            "bank_id": bank,
            "baseline_reused_across_stages": True,
            "synthetic_dataset": True,
        },
        synthetic=True,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    for dim in dimensions:
        db.add(
            EvaluationResult(
                organization_id=organization.id,
                run_id=run.id,
                dimension=dim["dimension"],
                score=dim["score"],
                explanation=dim["explanation"],
            )
        )
    db.commit()

    payload = _serialize_run(run, _results_for(db, run))
    payload["reused"] = False
    return payload


def experiment_summary(db: Session, organization: Organization, experiment_id: str | None = None) -> dict:
    runs = db.scalars(
        select(EvaluationRun)
        .where(EvaluationRun.organization_id == organization.id)
        .order_by(EvaluationRun.created_at)
    ).all()
    if experiment_id:
        runs = [r for r in runs if (r.details or {}).get("experiment_id") == experiment_id]
    else:
        ids = [(r.details or {}).get("experiment_id") for r in runs]
        ids = [i for i in ids if i]
        experiment_id = ids[-1] if ids else None
        if experiment_id:
            runs = [r for r in runs if (r.details or {}).get("experiment_id") == experiment_id]

    serialized = [_serialize_run(r, _results_for(db, r)) for r in runs]
    baseline = next((r for r in serialized if r["stage"] == 0), None)
    stages = [r for r in serialized if r["stage"] > 0]
    best = max(stages, key=lambda r: r["total_score"], default=None)
    latest = serialized[-1] if serialized else None
    return {
        "experiment_id": experiment_id,
        "question": LAB_QUESTION,
        "rubric": RUBRIC,
        "baseline": baseline,
        "stages": stages,
        "latest": latest,
        "improvement": {
            "baseline_score": baseline["total_score"] if baseline else None,
            "best_memory_score": best["total_score"] if best else None,
            "delta": round(best["total_score"] - baseline["total_score"], 2) if baseline and best else None,
            "best_stage": best["stage"] if best else None,
            "comparable": bool(baseline and best),
        },
        "valid_stages": list(VALID_STAGES),
        "dataset": "synthetic, labeled",
        "baseline_policy": "One stage-0 run with memory disabled, reused for every later comparison.",
        "engine": "Hindsight (self-hosted)",
    }


def experiments(db: Session, organization: Organization) -> list[dict]:
    runs = db.scalars(
        select(EvaluationRun)
        .where(EvaluationRun.organization_id == organization.id)
        .order_by(EvaluationRun.created_at.desc())
    ).all()
    grouped: dict[str, list[EvaluationRun]] = {}
    for run in runs:
        exp = (run.details or {}).get("experiment_id") or "unknown"
        grouped.setdefault(exp, []).append(run)
    payload = []
    for exp, items in grouped.items():
        baseline = next((r for r in items if r.stage == 0), None)
        memory_runs = [r for r in items if r.stage > 0]
        best = max(memory_runs, key=lambda r: r.total_score, default=None)
        payload.append(
            {
                "experiment_id": exp,
                "created_at": min(r.created_at for r in items).isoformat() if items else None,
                "stages_completed": sorted(r.stage for r in items),
                "baseline_score": baseline.total_score if baseline else None,
                "best_memory_score": best.total_score if best else None,
                "delta": round(best.total_score - baseline.total_score, 2) if baseline and best else None,
            }
        )
    payload.sort(key=lambda x: x["created_at"] or "", reverse=True)
    return payload
