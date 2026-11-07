"""Validated backend tools exposed to the LLM.

Every tool is scoped to the authenticated organization. The model supplies
arguments, never organization ids or SQL. Consequential operations create
auditable records and require human confirmation in the normal workflow.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..deps import audit
from ..models import (
    Alert,
    InventoryItem,
    Organization,
    ProcurementDecision,
    PurchaseOrder,
    QualityIncident,
    ScheduledAction,
    ShipmentEvent,
    Supplier,
    SupplierComplaint,
    User,
)
from ..schemas import ORDER_STATUSES
from . import memory as memory_service
from . import metrics as metrics_service
from . import monitoring


class ToolError(ValueError):
    pass


@dataclass
class ToolContext:
    db: Session
    organization: Organization
    user: User | None = None
    memory_bank_id: str | None = None


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _parse_date(value: str | None, *, default: datetime | None = None) -> datetime:
    if not value:
        if default is None:
            raise ToolError("A date is required")
        return default
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ToolError(f"Invalid ISO-8601 date: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def resolve_supplier(ctx: ToolContext, identifier: str) -> Supplier:
    ident = (identifier or "").strip()
    if not ident:
        raise ToolError("supplier identifier is required")
    try:
        supplier = ctx.db.get(Supplier, uuid.UUID(ident))
        if supplier and supplier.organization_id == ctx.organization.id:
            return supplier
    except ValueError:
        pass
    supplier = ctx.db.scalar(
        select(Supplier).where(
            Supplier.organization_id == ctx.organization.id,
            func.lower(Supplier.name) == ident.lower(),
        )
    )
    if supplier:
        return supplier
    supplier = ctx.db.scalar(
        select(Supplier).where(
            Supplier.organization_id == ctx.organization.id,
            Supplier.name.ilike(f"%{ident}%"),
        )
    )
    if supplier:
        return supplier
    raise ToolError(f"Supplier '{identifier}' was not found in this organization")


def resolve_order(ctx: ToolContext, identifier: str) -> PurchaseOrder:
    ident = (identifier or "").strip()
    try:
        order = ctx.db.get(PurchaseOrder, uuid.UUID(ident))
        if order and order.organization_id == ctx.organization.id:
            return order
    except ValueError:
        pass
    order = ctx.db.scalar(
        select(PurchaseOrder).where(
            PurchaseOrder.organization_id == ctx.organization.id,
            func.lower(PurchaseOrder.order_number) == ident.lower(),
        )
    )
    if order:
        return order
    raise ToolError(f"Order '{identifier}' was not found in this organization")


def _supplier_metrics(ctx: ToolContext, supplier: Supplier):
    return metrics_service.supplier_metrics_map(ctx.db, ctx.organization.id).get(supplier.id)


# ---------------------------------------------------------------------------
# read tools
# ---------------------------------------------------------------------------
def get_supplier_profile(ctx: ToolContext, supplier: str) -> dict:
    s = resolve_supplier(ctx, supplier)
    m = _supplier_metrics(ctx, s)
    orders = ctx.db.scalars(
        select(PurchaseOrder)
        .where(PurchaseOrder.organization_id == ctx.organization.id, PurchaseOrder.supplier_id == s.id)
        .order_by(PurchaseOrder.order_date.desc())
        .limit(5)
    ).all()
    complaints = ctx.db.scalars(
        select(SupplierComplaint)
        .where(SupplierComplaint.organization_id == ctx.organization.id, SupplierComplaint.supplier_id == s.id)
        .order_by(SupplierComplaint.reported_date.desc())
        .limit(6)
    ).all()
    incidents = ctx.db.scalars(
        select(QualityIncident)
        .where(QualityIncident.organization_id == ctx.organization.id, QualityIncident.supplier_id == s.id)
        .order_by(QualityIncident.occurred_at.desc())
        .limit(6)
    ).all()
    return {
        "supplier": {
            "id": str(s.id),
            "name": s.name,
            "location": ", ".join(x for x in [s.city, s.country] if x),
            "categories": s.categories,
            "promised_lead_days": s.promised_lead_days,
            "status": s.status,
        },
        "metrics": m.model_dump() if m else {},
        "recent_orders": [
            {
                "order_number": o.order_number,
                "product": o.product,
                "status": o.status,
                "promised_date": _iso(o.promised_date),
                "actual_arrival": _iso(o.actual_arrival),
                "delay_days": metrics_service.delay_days(o),
                "priority": o.priority,
            }
            for o in orders
        ],
        "complaints": [
            {
                "type": c.complaint_type,
                "severity": c.severity,
                "description": c.description,
                "reported_date": _iso(c.reported_date),
            }
            for c in complaints
        ],
        "quality_incidents": [
            {"severity": i.severity, "description": i.description, "occurred_at": _iso(i.occurred_at)}
            for i in incidents
        ],
    }


def get_supplier_order_history(ctx: ToolContext, supplier: str, limit: int = 8) -> dict:
    s = resolve_supplier(ctx, supplier)
    limit = max(1, min(int(limit or 8), 20))
    orders = ctx.db.scalars(
        select(PurchaseOrder)
        .where(PurchaseOrder.organization_id == ctx.organization.id, PurchaseOrder.supplier_id == s.id)
        .order_by(PurchaseOrder.order_date.desc())
        .limit(limit)
    ).all()
    return {
        "supplier": s.name,
        "orders": [
            {
                "order_number": o.order_number,
                "product": o.product,
                "quantity": o.quantity,
                "status": o.status,
                "order_date": _iso(o.order_date),
                "promised_date": _iso(o.promised_date),
                "actual_arrival": _iso(o.actual_arrival),
                "delay_days": metrics_service.delay_days(o),
                "priority": o.priority,
            }
            for o in orders
        ],
    }


def calculate_supplier_reliability(ctx: ToolContext, supplier: str) -> dict:
    s = resolve_supplier(ctx, supplier)
    m = _supplier_metrics(ctx, s)
    return {
        "supplier": s.name,
        "metrics": m.model_dump() if m else {},
        "method": (
            "reliability = 100 - min(40, avg_delay*4) - min(30, late_rate*30) "
            "- min(20, quality_issues*5) - min(10, communication_complaints*3) "
            "- min(10, transportation_incidents*2); calculated from PostgreSQL records"
        ),
        "note": "Historical facts, not a prediction of the next delivery.",
    }


def get_order_details(ctx: ToolContext, order_number: str) -> dict:
    o = resolve_order(ctx, order_number)
    s = ctx.db.get(Supplier, o.supplier_id)
    events = ctx.db.scalars(
        select(ShipmentEvent)
        .where(ShipmentEvent.order_id == o.id, ShipmentEvent.organization_id == ctx.organization.id)
        .order_by(ShipmentEvent.event_date)
    ).all()
    return {
        "order": {
            "id": str(o.id),
            "order_number": o.order_number,
            "supplier": s.name if s else None,
            "product": o.product,
            "quantity": o.quantity,
            "status": o.status,
            "priority": o.priority,
            "order_date": _iso(o.order_date),
            "promised_date": _iso(o.promised_date),
            "estimated_arrival": _iso(o.estimated_arrival),
            "actual_arrival": _iso(o.actual_arrival),
            "delay_days": metrics_service.delay_days(o),
            "destination": o.destination,
            "transport_mode": o.transport_mode,
            "tracking_reference": o.tracking_reference,
            "financial_impact": o.financial_impact,
            "risk_level": metrics_service.risk_level_for(o, _supplier_metrics(ctx, s) if s else None),
        },
        "shipment_events": [
            {
                "event_type": e.event_type,
                "event_date": _iso(e.event_date),
                "location": e.location,
                "description": e.description,
                "source": e.source,
            }
            for e in events
        ],
    }


def get_shipment_events(ctx: ToolContext, order_number: str) -> dict:
    o = resolve_order(ctx, order_number)
    events = ctx.db.scalars(
        select(ShipmentEvent)
        .where(ShipmentEvent.order_id == o.id, ShipmentEvent.organization_id == ctx.organization.id)
        .order_by(ShipmentEvent.event_date)
    ).all()
    return {
        "order_number": o.order_number,
        "status": o.status,
        "events": [
            {
                "event_type": e.event_type,
                "event_date": _iso(e.event_date),
                "location": e.location,
                "description": e.description,
            }
            for e in events
        ],
    }


def identify_bottlenecks(ctx: ToolContext) -> dict:
    items = metrics_service.bottlenecks(ctx.db, ctx.organization.id)
    return {"count": len(items), "bottlenecks": items[:8]}


def compare_suppliers(ctx: ToolContext, suppliers: list[str], requirements: str | None = None) -> dict:
    if not suppliers:
        raise ToolError("At least one supplier is required")
    rows = []
    for name in suppliers[:6]:
        s = resolve_supplier(ctx, name)
        m = _supplier_metrics(ctx, s)
        rows.append(
            {
                "id": str(s.id),
                "name": s.name,
                "metrics": m.model_dump() if m else {},
                "promised_lead_days": s.promised_lead_days,
            }
        )
    ranked = sorted(rows, key=lambda r: r["metrics"].get("reliability_score", 0), reverse=True)
    return {"requirements": requirements, "comparison": ranked, "deterministic_ranking": True}


def list_pending_alerts(ctx: ToolContext) -> dict:
    alerts = ctx.db.scalars(
        select(Alert)
        .where(Alert.organization_id == ctx.organization.id, Alert.status.in_(["open", "acknowledged"]))
        .order_by(Alert.created_at.desc())
        .limit(20)
    ).all()
    return {
        "count": len(alerts),
        "alerts": [
            {
                "id": str(a.id),
                "type": a.alert_type,
                "severity": a.severity,
                "title": a.title,
                "order_id": str(a.order_id) if a.order_id else None,
                "due_at": _iso(a.due_at),
            }
            for a in alerts
        ],
    }


def evaluate_contingency_options(ctx: ToolContext, supplier: str, disruption_days: int = 10) -> dict:
    s = resolve_supplier(ctx, supplier)
    days = max(1, min(int(disruption_days), 120))
    affected = ctx.db.scalars(
        select(PurchaseOrder).where(
            PurchaseOrder.organization_id == ctx.organization.id,
            PurchaseOrder.supplier_id == s.id,
            PurchaseOrder.status.in_(["created", "confirmed", "processing", "dispatched", "in_transit", "delayed"]),
        )
    ).all()
    metrics = metrics_service.supplier_metrics_map(ctx.db, ctx.organization.id)
    alternatives = []
    for other in ctx.db.scalars(
        select(Supplier).where(Supplier.organization_id == ctx.organization.id, Supplier.id != s.id)
    ).all():
        m = metrics.get(other.id)
        if m and m.reliability_score >= 60:
            alternatives.append(
                {"id": str(other.id), "name": other.name, "reliability_score": m.reliability_score,
                 "avg_delay_days": m.avg_delay_days, "on_time_rate": m.on_time_rate,
                 "promised_lead_days": other.promised_lead_days}
            )
    alternatives.sort(key=lambda a: a["reliability_score"], reverse=True)
    return {
        "scenario": f"{s.name} cannot deliver for {days} additional days",
        "simulated": True,
        "affected_orders": [
            {
                "order_number": o.order_number,
                "product": o.product,
                "priority": o.priority,
                "promised_date": _iso(o.promised_date),
                "financial_impact": o.financial_impact,
                "already_delayed_days": metrics_service.delay_days(o),
            }
            for o in affected
        ],
        "financial_exposure": round(sum(o.financial_impact for o in affected), 2),
        "alternatives": alternatives[:5],
        "assumptions": [
            "Historical performance is used as a risk indicator, not a guarantee.",
            "Alternative suppliers are ranked only on verified historical records.",
        ],
    }


# ---------------------------------------------------------------------------
# write tools
# ---------------------------------------------------------------------------
def _next_order_number(ctx: ToolContext) -> str:
    count = ctx.db.scalar(
        select(func.count(PurchaseOrder.id)).where(PurchaseOrder.organization_id == ctx.organization.id)
    )
    candidate = f"PO-{1000 + int(count or 0) + 1}"
    while ctx.db.scalar(
        select(PurchaseOrder.id).where(
            PurchaseOrder.organization_id == ctx.organization.id,
            PurchaseOrder.order_number == candidate,
        )
    ):
        candidate = f"PO-{int(candidate.split('-')[1]) + 1}"
    return candidate


def create_purchase_order(
    ctx: ToolContext,
    supplier: str,
    product: str,
    quantity: int,
    promised_date: str,
    priority: str = "normal",
    destination: str | None = None,
    transport_mode: str = "road",
    financial_impact: float = 0.0,
) -> dict:
    s = resolve_supplier(ctx, supplier)
    if int(quantity) <= 0:
        raise ToolError("quantity must be positive")
    if priority not in {"low", "normal", "high", "critical"}:
        raise ToolError("priority must be low, normal, high or critical")
    if transport_mode not in {"road", "rail", "air", "sea", "multimodal"}:
        raise ToolError("invalid transport_mode")
    promised = _parse_date(promised_date)
    order = PurchaseOrder(
        organization_id=ctx.organization.id,
        supplier_id=s.id,
        order_number=_next_order_number(ctx),
        product=product.strip(),
        quantity=int(quantity),
        order_date=datetime.now(timezone.utc),
        promised_date=promised,
        estimated_arrival=promised,
        status="created",
        priority=priority,
        destination=destination,
        transport_mode=transport_mode,
        financial_impact=max(0.0, float(financial_impact or 0)),
        notes="Created by the AI procurement assistant. A human must confirm before commitment.",
    )
    ctx.db.add(order)
    ctx.db.commit()
    ctx.db.refresh(order)
    monitoring.schedule_order_monitoring(ctx.db, order)
    audit(
        ctx.db,
        ctx.organization.id,
        ctx.user.id if ctx.user else None,
        "agent.create_purchase_order",
        "purchase_order",
        str(order.id),
        {"order_number": order.order_number, "requires_human_confirmation": True},
    )
    ctx.db.commit()
    return {
        "created": True,
        "requires_human_confirmation": True,
        "order": {
            "id": str(order.id),
            "order_number": order.order_number,
            "supplier": s.name,
            "product": order.product,
            "quantity": order.quantity,
            "promised_date": _iso(order.promised_date),
            "status": order.status,
            "priority": order.priority,
        },
        "monitoring": "Risk-aware checkpoints scheduled in PostgreSQL.",
        "human_action": "Confirm or cancel this draft in the Orders screen before sending it to the supplier.",
    }


def update_order_status(ctx: ToolContext, order_number: str, status: str, note: str | None = None) -> dict:
    if status not in ORDER_STATUSES:
        raise ToolError(f"status must be one of {ORDER_STATUSES}")
    order = resolve_order(ctx, order_number)
    order.status = status
    if status == "delivered":
        order.actual_arrival = datetime.now(timezone.utc)
    ctx.db.commit()
    monitoring.reschedule_order_monitoring(ctx.db, order)

    retained = False
    if status == "delivered":
        s = ctx.db.get(Supplier, order.supplier_id)
        content = (
            f"Verified outcome for order {order.order_number} from {s.name if s else 'supplier'}: "
            f"promised {order.promised_date.date().isoformat()}, delivered "
            f"{order.actual_arrival.date().isoformat()}, delay {metrics_service.delay_days(order)} days. "
            f"Product {order.product}, quantity {order.quantity}. {note or ''}"
        ).strip()
        try:
            memory_service.retain(
                ctx.db,
                ctx.organization,
                content=content,
                category="outcome",
                source_type="verified_business_fact",
                supplier_id=order.supplier_id,
                order_id=order.id,
                event_date=order.actual_arrival,
                context="delivery outcome",
                bank_id=ctx.memory_bank_id,
                record_provenance=ctx.memory_bank_id is None,
            )
            retained = True
        except Exception:  # noqa: BLE001
            retained = False

    audit(
        ctx.db,
        ctx.organization.id,
        ctx.user.id if ctx.user else None,
        "agent.update_order_status",
        "purchase_order",
        str(order.id),
        {"status": status, "note": note},
    )
    ctx.db.commit()
    return {
        "updated": True,
        "order_number": order.order_number,
        "status": order.status,
        "outcome_retained_in_hindsight": retained,
    }


def create_followup(ctx: ToolContext, order_number: str, days: int = 2, note: str | None = None) -> dict:
    order = resolve_order(ctx, order_number)
    days = max(1, min(int(days), 60))
    run_at = datetime.now(timezone.utc) + timedelta(days=days)
    dedupe = f"followup:{order.id}:{run_at.date().isoformat()}"
    action = monitoring._add_action(
        ctx.db,
        ctx.organization.id,
        order.id,
        "supplier_confirmation",
        run_at,
        dedupe,
        {"note": note or "Agent-created follow-up", "avg_delay": 0},
    )
    ctx.db.commit()
    return {
        "created": True,
        "order_number": order.order_number,
        "run_at": run_at.isoformat(),
        "note": note or "Follow up with the supplier for a dated confirmation.",
        "persistent": True,
    }


# ---------------------------------------------------------------------------
# memory tools
# ---------------------------------------------------------------------------
def retrieve_company_memory(ctx: ToolContext, query: str, max_tokens: int = 3000) -> dict:
    result = memory_service.recall(
        ctx.db,
        ctx.organization,
        query=query,
        max_tokens=max_tokens,
        budget="mid",
        bank_id=ctx.memory_bank_id,
    )
    return {
        "result_count": result["result_count"],
        "memories": [
            {
                "text": h["text"][:700],
                "type": h.get("type"),
                "score": h.get("score"),
                "provenance": h.get("provenance"),
            }
            for h in result["results"][:10]
        ],
    }


def retain_business_experience(
    ctx: ToolContext,
    content: str,
    category: str = "episodic",
    supplier: str | None = None,
    order_number: str | None = None,
    source_type: str = "user_reported_fact",
) -> dict:
    if category not in {"episodic", "semantic", "decision", "outcome", "preference", "future_action"}:
        raise ToolError("invalid memory category")
    if source_type not in {
        "verified_business_fact",
        "user_reported_fact",
        "imported_external_observation",
        "ai_inference",
        "recommendation",
    }:
        raise ToolError("invalid source_type")
    supplier_obj = resolve_supplier(ctx, supplier) if supplier else None
    order_obj = resolve_order(ctx, order_number) if order_number else None
    # Guard: an AI inference can never be stored as a verified business fact.
    if source_type == "verified_business_fact" and not (supplier_obj or order_obj):
        raise ToolError("verified business facts must reference an existing supplier or order")
    result = memory_service.retain(
        ctx.db,
        ctx.organization,
        content=content,
        category=category,
        source_type=source_type,
        supplier_id=supplier_obj.id if supplier_obj else None,
        order_id=order_obj.id if order_obj else None,
        event_date=datetime.now(timezone.utc),
        confidence=0.9 if source_type != "verified_business_fact" else 1.0,
        bank_id=ctx.memory_bank_id,
        record_provenance=ctx.memory_bank_id is None,
    )
    return {
        "retained": True,
        "category": category,
        "source_type": source_type,
        "document_id": result["document_id"],
        "latency_ms": result["latency_ms"],
    }


def reflect_on_supplier_history(ctx: ToolContext, supplier: str, question: str) -> dict:
    s = resolve_supplier(ctx, supplier)
    result = memory_service.reflect(
        ctx.db,
        ctx.organization,
        query=question,
        context=f"Reflect on the historical performance of {s.name}",
        budget="mid",
        supplier_id=s.id,
        bank_id=ctx.memory_bank_id,
    )
    return {"supplier": s.name, "reflection": result["text"][:2500], "based_on": result.get("based_on")}


TOOL_FUNCTIONS: dict[str, Callable[..., dict]] = {
    "get_supplier_profile": get_supplier_profile,
    "get_supplier_order_history": get_supplier_order_history,
    "calculate_supplier_reliability": calculate_supplier_reliability,
    "get_order_details": get_order_details,
    "get_shipment_events": get_shipment_events,
    "identify_bottlenecks": identify_bottlenecks,
    "compare_suppliers": compare_suppliers,
    "list_pending_alerts": list_pending_alerts,
    "evaluate_contingency_options": evaluate_contingency_options,
    "create_purchase_order": create_purchase_order,
    "update_order_status": update_order_status,
    "create_followup": create_followup,
    "retrieve_company_memory": retrieve_company_memory,
    "retain_business_experience": retain_business_experience,
    "reflect_on_supplier_history": reflect_on_supplier_history,
}


def tool_schemas() -> list[dict]:
    """Groq/OpenAI-compatible function schemas for the validated tools."""
    def fn(name: str, description: str, properties: dict, required: list[str]) -> dict:
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {"type": "object", "properties": properties, "required": required},
            },
        }

    return [
        fn("get_supplier_profile", "Get a supplier profile with deterministic delivery, quality and complaint metrics.",
           {"supplier": {"type": "string", "description": "Supplier name or id"}}, ["supplier"]),
        fn("get_supplier_order_history", "Get recent purchase orders and actual delay days for a supplier.",
           {"supplier": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 20}}, ["supplier"]),
        fn("calculate_supplier_reliability", "Calculate on-time rate, average delay and reliability score from database records.",
           {"supplier": {"type": "string"}}, ["supplier"]),
        fn("get_order_details", "Get one order, its risk level and shipment events.",
           {"order_number": {"type": "string"}}, ["order_number"]),
        fn("get_shipment_events", "Read shipment events for an order.",
           {"order_number": {"type": "string"}}, ["order_number"]),
        fn("identify_bottlenecks", "List deterministic supply-chain bottlenecks and evidence.", {}, []),
        fn("compare_suppliers", "Compare several suppliers using deterministic historical metrics.",
           {"suppliers": {"type": "array", "items": {"type": "string"}}, "requirements": {"type": "string"}}, ["suppliers"]),
        fn("list_pending_alerts", "List open and acknowledged alerts.", {}, []),
        fn("evaluate_contingency_options", "Simulate a supplier disruption and list verified alternatives.",
           {"supplier": {"type": "string"}, "disruption_days": {"type": "integer", "minimum": 1, "maximum": 120}},
           ["supplier", "disruption_days"]),
        fn("create_purchase_order", "Create a DRAFT purchase order that a human must confirm. Never invent shipment updates.",
           {
               "supplier": {"type": "string"}, "product": {"type": "string"},
               "quantity": {"type": "integer", "minimum": 1},
               "promised_date": {"type": "string", "description": "ISO-8601 date or datetime"},
               "priority": {"type": "string", "enum": ["low", "normal", "high", "critical"]},
               "destination": {"type": "string"},
               "transport_mode": {"type": "string", "enum": ["road", "rail", "air", "sea", "multimodal"]},
               "financial_impact": {"type": "number", "minimum": 0},
           }, ["supplier", "product", "quantity", "promised_date"]),
        fn("update_order_status", "Update an order status. Delivered outcomes are retained in Hindsight.",
           {"order_number": {"type": "string"}, "status": {"type": "string", "enum": ORDER_STATUSES}, "note": {"type": "string"}},
           ["order_number", "status"]),
        fn("create_followup", "Create a persistent follow-up action for an order.",
           {"order_number": {"type": "string"}, "days": {"type": "integer", "minimum": 1, "maximum": 60}, "note": {"type": "string"}},
           ["order_number"]),
        fn("retrieve_company_memory", "Recall relevant organizational memories from Hindsight.",
           {"query": {"type": "string"}, "max_tokens": {"type": "integer", "minimum": 256, "maximum": 8000}}, ["query"]),
        fn("retain_business_experience", "Retain a meaningful experience in Hindsight. Never mark an inference as verified.",
           {
               "content": {"type": "string"},
               "category": {"type": "string", "enum": ["episodic", "semantic", "decision", "outcome", "preference", "future_action"]},
               "supplier": {"type": "string"}, "order_number": {"type": "string"},
               "source_type": {"type": "string", "enum": ["verified_business_fact", "user_reported_fact", "imported_external_observation", "ai_inference", "recommendation"]},
           }, ["content"]),
        fn("reflect_on_supplier_history", "Use Hindsight reflect to reason over a supplier's history.",
           {"supplier": {"type": "string"}, "question": {"type": "string"}}, ["supplier", "question"]),
    ]


def execute_tool(name: str, arguments: dict[str, Any], ctx: ToolContext) -> dict:
    fn = TOOL_FUNCTIONS.get(name)
    if not fn:
        raise ToolError(f"Unknown tool: {name}")
    try:
        return fn(ctx, **(arguments or {}))
    except ToolError:
        raise
    except TypeError as exc:
        raise ToolError(f"Invalid arguments for {name}: {exc}") from exc


def summarize_result(result: dict, max_chars: int = 900) -> str:
    try:
        text = json.dumps(result, default=str, ensure_ascii=False)
    except Exception:  # noqa: BLE001
        text = str(result)
    return text[:max_chars]
