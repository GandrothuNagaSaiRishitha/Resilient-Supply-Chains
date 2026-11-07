"""Hindsight memory engine integration.

Hindsight is the only persistent agent memory in SUPPLYMIND. This module wraps
the official `hindsight-client` SDK. Every operation is executed against a live
Hindsight server and recorded in `memory_operation_logs` for audit. PostgreSQL
tables store business records and a local provenance index, never a substitute
for Hindsight retrieval.
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from hindsight_client import Hindsight
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import MemoryOperationLog, MemoryRecord, Organization, Supplier
from ..schemas import MemoryHit

settings = get_settings()
logger = logging.getLogger("supplymind.memory")


class HindsightUnavailable(RuntimeError):
    pass


def _client() -> Hindsight:
    return Hindsight(base_url=settings.hindsight_base_url, timeout=settings.hindsight_timeout_seconds)


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def bank_for(organization: Organization, bank_id: str | None = None) -> str:
    """Return the server-controlled Hindsight bank id for an organization.

    Bank ids are never accepted from clients; they are generated at organization
    creation and stored on the organization row. The optional ``bank_id`` argument
    exists only for server-derived banks such as the Memory Learning Lab bank
    (``<org bank>__lab``), which is computed on the server and never accepted
    from a request body.
    """
    return bank_id or organization.memory_bank_id


def ensure_bank(organization: Organization, bank_id: str | None = None) -> None:
    bank = bank_for(organization, bank_id)
    label = "Memory Learning Lab" if bank.endswith("__lab") else "organizational memory"
    client = _client()
    mission = (
        "You are the organizational supply-chain memory for "
        f"{organization.name}. Remember verified supplier delivery history, "
        "quality and communication issues, transportation incidents, procurement "
        "decisions and their outcomes, and company procurement preferences. "
        "Separate verified facts from inferences and recommendations. Never invent "
        "a supplier fact. Prefer recent, verified evidence when answering."
    )
    # Curated business experiences are stored as exact chunks. This preserves the
    # wording of every fact (no generative rewriting) and avoids spending the
    # free-tier LLM quota on extraction for text that is already structured.
    bank_options = {
        "retain_extraction_mode": "chunks",
        "enable_observations": False,
        "enable_text_search": True,
        "enable_temporal_retrieval": True,
        "enable_reranking": True,
    }
    try:
        client.create_bank(
            bank_id=bank,
            name=f"{organization.name} - SUPPLYMIND {label}",
            mission=mission,
            disposition={"skepticism": 4, "literalism": 4, "empathy": 2},
            **bank_options,
        )
        return
    except Exception:  # bank may already exist; Hindsight returns a conflict
        pass
    try:
        client.update_bank_config(bank_id=bank, **bank_options)
    except Exception:  # config API may be disabled; creation defaults still apply
        pass


def _log(
    db: Session,
    organization: Organization,
    operation: str,
    status: str,
    *,
    bank_id: str | None = None,
    query: str | None = None,
    content_summary: str | None = None,
    supplier_id: uuid.UUID | None = None,
    order_id: uuid.UUID | None = None,
    source_type: str | None = None,
    verified: bool | None = None,
    result_count: int | None = None,
    latency_ms: int | None = None,
    detail: dict | None = None,
    error: str | None = None,
) -> MemoryOperationLog:
    row = MemoryOperationLog(
        organization_id=organization.id,
        bank_id=bank_for(organization, bank_id),
        operation=operation,
        status=status,
        query=query,
        content_summary=(content_summary or "")[:2000] or None,
        related_supplier_id=supplier_id,
        related_order_id=order_id,
        source_type=source_type,
        verified=verified,
        result_count=result_count,
        latency_ms=latency_ms,
        detail=detail or {},
        error=(error or "")[:4000] or None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def retain(
    db: Session,
    organization: Organization,
    *,
    content: str,
    category: str = "episodic",
    source_type: str = "verified_business_fact",
    context: str | None = None,
    supplier_id: uuid.UUID | None = None,
    order_id: uuid.UUID | None = None,
    event_date: datetime | None = None,
    confidence: float = 1.0,
    document_id: str | None = None,
    synthetic: bool = False,
    metadata: dict | None = None,
    bank_id: str | None = None,
    record_provenance: bool = True,
) -> dict:
    """Retain a meaningful, validated business experience in Hindsight."""
    bank = bank_for(organization, bank_id)
    document_id = document_id or str(uuid.uuid4())
    meta = {
        "company_id": str(organization.id),
        "bank_id": bank,
        "memory_category": category,
        "source_type": source_type,
        "verified": source_type == "verified_business_fact",
        "confidence": confidence,
        "supplier_id": str(supplier_id) if supplier_id else None,
        "order_id": str(order_id) if order_id else None,
        "event_date": (_aware(event_date) or datetime.now(timezone.utc)).isoformat(),
        **(metadata or {}),
    }
    started = time.perf_counter()
    try:
        client = _client()
        last_exc: Exception | None = None
        result = None
        for attempt in range(2):
            try:
                result = client.retain(
                    bank_id=bank,
                    content=content,
                    context=context or f"{category} organizational experience",
                    timestamp=_aware(event_date) or datetime.now(timezone.utc),
                    document_id=document_id,
                    metadata={k: str(v) for k, v in meta.items() if v is not None},
                    retain_async=False,
                )
                break
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                text = str(exc).lower()
                transient = any(token in text for token in ("429", "500", "502", "503", "quota", "timeout"))
                if attempt == 0 and transient:
                    time.sleep(4.0)
                    continue
                raise
        latency = int((time.perf_counter() - started) * 1000)
        record = None
        if record_provenance:
            record = MemoryRecord(
                organization_id=organization.id,
                bank_id=bank,
                hindsight_document_id=document_id,
                category=category,
                content=content,
                source_type=source_type,
                verified=source_type == "verified_business_fact",
                confidence=confidence,
                supplier_id=supplier_id,
                order_id=order_id,
                event_date=_aware(event_date),
                metadata_json=meta,
                synthetic=synthetic,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
        log = _log(
            db,
            organization,
            "retain",
            "success",
            bank_id=bank,
            content_summary=content[:400],
            supplier_id=supplier_id,
            order_id=order_id,
            source_type=source_type,
            verified=source_type == "verified_business_fact" if record is None else record.verified,
            latency_ms=latency,
            detail={"document_id": document_id, "category": category, "hindsight_result": str(result)[:1000]},
        )
        return {
            "operation": "retain",
            "status": "success",
            "bank_id": bank,
            "document_id": document_id,
            "record_id": str(record.id) if record else None,
            "operation_log_id": str(log.id),
            "latency_ms": latency,
        }
    except Exception as exc:  # noqa: BLE001
        latency = int((time.perf_counter() - started) * 1000)
        _log(
            db,
            organization,
            "retain",
            "error",
            bank_id=bank,
            content_summary=content[:400],
            supplier_id=supplier_id,
            order_id=order_id,
            source_type=source_type,
            verified=source_type == "verified_business_fact",
            latency_ms=latency,
            error=str(exc),
        )
        raise HindsightUnavailable(f"Hindsight retain failed: {exc}") from exc


def recall(
    db: Session,
    organization: Organization,
    *,
    query: str,
    types: list[str] | None = None,
    max_tokens: int | None = None,
    budget: str = "mid",
    supplier_id: uuid.UUID | None = None,
    order_id: uuid.UUID | None = None,
    bank_id: str | None = None,
) -> dict:
    bank = bank_for(organization, bank_id)
    started = time.perf_counter()
    try:
        client = _client()
        response = client.recall(
            bank_id=bank,
            query=query,
            types=types,
            max_tokens=max_tokens or 4096,
            budget=budget,
        )
        latency = int((time.perf_counter() - started) * 1000)
        hits: list[dict] = []
        doc_ids: list[str] = []
        for r in response.results:
            metadata = getattr(r, "metadata", None) or {}
            scores = getattr(r, "scores", None)
            score = getattr(scores, "final", None) if scores else None
            doc_id = getattr(r, "document_id", None)
            if doc_id:
                doc_ids.append(str(doc_id))
            hits.append(
                {
                    "id": str(getattr(r, "id", "")) or None,
                    "text": getattr(r, "text", ""),
                    "type": getattr(r, "type", None),
                    "score": round(float(score), 4) if score is not None else None,
                    "metadata": metadata,
                    "document_id": str(doc_id) if doc_id else None,
                    "occurred_start": str(getattr(r, "occurred_start", "") or "") or None,
                    "context": getattr(r, "context", None),
                }
            )

        # Enrich with local provenance records where the document id matches.
        if doc_ids:
            records = db.scalars(
                select(MemoryRecord).where(
                    MemoryRecord.organization_id == organization.id,
                    MemoryRecord.bank_id == bank,
                    MemoryRecord.hindsight_document_id.in_(doc_ids),
                )
            ).all()
            by_doc = {rec.hindsight_document_id: rec for rec in records}
            for hit in hits:
                rec = by_doc.get(hit.get("document_id"))
                if rec:
                    hit["provenance"] = {
                        "category": rec.category,
                        "source_type": rec.source_type,
                        "verified": rec.verified,
                        "confidence": rec.confidence,
                        "supplier_id": str(rec.supplier_id) if rec.supplier_id else None,
                        "order_id": str(rec.order_id) if rec.order_id else None,
                        "event_date": rec.event_date.isoformat() if rec.event_date else None,
                        "record_id": str(rec.id),
                        "crisis_type": rec.metadata_json.get("crisis_type"),
                        "strategy_key": rec.metadata_json.get("strategy_key"),
                        "successful": rec.metadata_json.get("successful"),
                        "lessons_learned": rec.metadata_json.get("lessons_learned"),
                        "incident_title": rec.metadata_json.get("incident_title"),
                        "expected_result": rec.metadata_json.get("expected_result"),
                    }

        log = _log(
            db,
            organization,
            "recall",
            "success",
            bank_id=bank,
            query=query,
            supplier_id=supplier_id,
            order_id=order_id,
            result_count=len(hits),
            latency_ms=latency,
            detail={"types": types, "budget": budget, "top_score": hits[0]["score"] if hits else None},
        )
        return {
            "operation": "recall",
            "status": "success",
            "bank_id": bank,
            "result_count": len(hits),
            "latency_ms": latency,
            "results": hits,
            "operation_log_id": str(log.id),
        }
    except Exception as exc:  # noqa: BLE001
        latency = int((time.perf_counter() - started) * 1000)
        _log(
            db,
            organization,
            "recall",
            "error",
            bank_id=bank,
            query=query,
            supplier_id=supplier_id,
            order_id=order_id,
            latency_ms=latency,
            error=str(exc),
        )
        raise HindsightUnavailable(f"Hindsight recall failed: {exc}") from exc


def reflect(
    db: Session,
    organization: Organization,
    *,
    query: str,
    context: str | None = None,
    budget: str = "mid",
    supplier_id: uuid.UUID | None = None,
    order_id: uuid.UUID | None = None,
    bank_id: str | None = None,
) -> dict:
    bank = bank_for(organization, bank_id)
    started = time.perf_counter()
    try:
        client = _client()
        answer = None
        last_exc: Exception | None = None
        for attempt in range(2):
            try:
                answer = client.reflect(
                    bank_id=bank,
                    query=query,
                    context=context,
                    budget=budget,
                )
                break
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                text = str(exc).lower()
                transient = any(
                    token in text
                    for token in ("429", "500", "502", "503", "quota", "rate limit", "timeout", "capacity")
                )
                if attempt == 0 and transient:
                    logger.warning("Hindsight reflect transient failure, retrying once: %s", exc)
                    time.sleep(8.0)
                    continue
                raise
        if answer is None and last_exc is not None:  # pragma: no cover - defensive
            raise last_exc
        latency = int((time.perf_counter() - started) * 1000)
        based_on = getattr(answer, "based_on", None)
        usage = getattr(answer, "usage", None)
        detail = {
            "based_on": _jsonable(based_on),
            "usage": _jsonable(usage),
        }
        log = _log(
            db,
            organization,
            "reflect",
            "success",
            bank_id=bank,
            query=query,
            supplier_id=supplier_id,
            order_id=order_id,
            result_count=len(_jsonable(based_on) or []) if isinstance(_jsonable(based_on), list) else 0,
            latency_ms=latency,
            detail=detail,
        )
        return {
            "operation": "reflect",
            "status": "success",
            "bank_id": bank,
            "text": getattr(answer, "text", ""),
            "based_on": _jsonable(based_on),
            "usage": _jsonable(usage),
            "latency_ms": latency,
            "operation_log_id": str(log.id),
        }
    except Exception as exc:  # noqa: BLE001
        latency = int((time.perf_counter() - started) * 1000)
        _log(
            db,
            organization,
            "reflect",
            "error",
            bank_id=bank,
            query=query,
            supplier_id=supplier_id,
            order_id=order_id,
            latency_ms=latency,
            error=str(exc),
        )
        raise HindsightUnavailable(f"Hindsight reflect failed: {exc}") from exc


def lab_bank_id(organization: Organization) -> str:
    """Server-derived, isolated Hindsight bank used by the Memory Learning Lab.

    The lab never writes into, or resets, the production organizational bank.
    """
    return f"{organization.memory_bank_id}__lab"


def overview(db: Session, organization: Organization) -> dict:
    bank = bank_for(organization)
    records = db.scalars(
        select(MemoryRecord).where(
            MemoryRecord.organization_id == organization.id,
            MemoryRecord.bank_id == bank,
        )
    ).all()
    logs = db.scalars(
        select(MemoryOperationLog)
        .where(
            MemoryOperationLog.organization_id == organization.id,
            MemoryOperationLog.bank_id == bank,
        )
        .order_by(MemoryOperationLog.created_at.desc())
        .limit(200)
    ).all()

    by_category: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for r in records:
        by_category[r.category] = by_category.get(r.category, 0) + 1
        by_source[r.source_type] = by_source.get(r.source_type, 0) + 1

    return {
        "bank_id": bank,
        "engine": "Hindsight (self-hosted)",
        "base_url": settings.hindsight_base_url,
        "retained_documents": len(records),
        "categories": by_category,
        "source_types": by_source,
        "operations": {
            "retain": sum(1 for log in logs if log.operation == "retain"),
            "recall": sum(1 for log in logs if log.operation == "recall"),
            "reflect": sum(1 for log in logs if log.operation == "reflect"),
            "errors": sum(1 for log in logs if log.status == "error"),
        },
        "last_operations": [_log_json(log) for log in logs[:20]],
    }


def history(db: Session, organization: Organization, limit: int = 100) -> list[dict]:
    logs = db.scalars(
        select(MemoryOperationLog)
        .where(
            MemoryOperationLog.organization_id == organization.id,
            MemoryOperationLog.bank_id == bank_for(organization),
        )
        .order_by(MemoryOperationLog.created_at.desc())
        .limit(limit)
    ).all()
    return [_log_json(log) for log in logs]


def records(db: Session, organization: Organization, limit: int = 200) -> list[dict]:
    rows = db.scalars(
        select(MemoryRecord)
        .where(
            MemoryRecord.organization_id == organization.id,
            MemoryRecord.bank_id == bank_for(organization),
        )
        .order_by(MemoryRecord.created_at.desc())
        .limit(limit)
    ).all()
    supplier_names = {
        s.id: s.name
        for s in db.scalars(select(Supplier).where(Supplier.organization_id == organization.id)).all()
    }
    return [
        {
            "id": str(r.id),
            "category": r.category,
            "content": r.content,
            "source_type": r.source_type,
            "verified": r.verified,
            "confidence": r.confidence,
            "supplier_id": str(r.supplier_id) if r.supplier_id else None,
            "supplier": supplier_names.get(r.supplier_id),
            "order_id": str(r.order_id) if r.order_id else None,
            "event_date": r.event_date.isoformat() if r.event_date else None,
            "document_id": r.hindsight_document_id,
            "metadata": r.metadata_json or {},
            "synthetic": r.synthetic,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


def reset_bank(db: Session, organization: Organization, bank_id: str | None = None) -> None:
    """Delete only the selected Hindsight bank and its local provenance rows.

    The Memory Learning Lab passes its isolated ``__lab`` bank. Production
    organization banks are never touched by another organization's request.
    """
    bank = bank_for(organization, bank_id)
    client = _client()
    try:
        client.delete_bank(bank)
    except Exception:  # noqa: BLE001
        pass
    ensure_bank(organization, bank)
    for row in db.scalars(
        select(MemoryRecord).where(
            MemoryRecord.organization_id == organization.id,
            MemoryRecord.bank_id == bank,
        )
    ).all():
        db.delete(row)
    db.commit()


def _log_json(log: MemoryOperationLog) -> dict:
    return {
        "id": str(log.id),
        "operation": log.operation,
        "status": log.status,
        "bank_id": log.bank_id,
        "query": log.query,
        "content_summary": log.content_summary,
        "related_supplier_id": str(log.related_supplier_id) if log.related_supplier_id else None,
        "related_order_id": str(log.related_order_id) if log.related_order_id else None,
        "source_type": log.source_type,
        "verified": log.verified,
        "result_count": log.result_count,
        "latency_ms": log.latency_ms,
        "detail": log.detail,
        "error": log.error,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


def _jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "model_dump"):
        return _jsonable(value.model_dump())
    if hasattr(value, "__dict__"):
        return {k: _jsonable(v) for k, v in value.__dict__.items() if not k.startswith("_")}
    return str(value)
