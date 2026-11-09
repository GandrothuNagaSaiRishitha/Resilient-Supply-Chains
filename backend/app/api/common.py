"""Shared serializers and lookup helpers for API routers."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
import re
from typing import Literal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import InventoryItem, Organization, PurchaseOrder, ShipmentEvent, Supplier, SupplierComplaint
from ..schemas import SupplierMetrics
from ..services import metrics as metrics_service


@dataclass(frozen=True)
class InventoryLookup:
    status: Literal["matched", "unmapped", "ambiguous"]
    items: tuple[InventoryItem, ...]
    detail: str

    def __iter__(self):
        return iter(self.items)

    def __eq__(self, other):
        if isinstance(other, list):
            return list(self.items) == other
        return super().__eq__(other)


def iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def supplier_metrics(db: Session, organization_id: uuid.UUID) -> dict[uuid.UUID, SupplierMetrics]:
    return metrics_service.supplier_metrics_map(db, organization_id)


@dataclass(frozen=True)
class InventoryMatch:
    """The result of resolving an incident component to canonical inventory."""

    items: tuple[InventoryItem, ...]
    status: str
    reason: str
    matched_sku: str | None = None


def _canonical(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").casefold())


def resolve_inventory_for_component(
    db: Session,
    organization_id: uuid.UUID,
    supplier_id: uuid.UUID | None,
    product_component: str,
) -> InventoryMatch:
    """Resolve a component description to exact, tenant-scoped inventory."""
    component = (product_component or "").strip()
    query = select(InventoryItem).where(InventoryItem.organization_id == organization_id)
    if supplier_id:
        query = query.where(InventoryItem.supplier_id == supplier_id)
    items = db.scalars(query.order_by(InventoryItem.name, InventoryItem.sku).limit(2000)).all()
    if not component:
        return InventoryMatch((), "missing", "The incident has no product or SKU description.")

    by_sku: dict[str, list[InventoryItem]] = {}
    for item in items:
        sku = _canonical(item.sku)
        if sku:
            by_sku.setdefault(sku, []).append(item)
    exact_sku = by_sku.get(_canonical(component), [])
    if len(exact_sku) == 1:
        item = exact_sku[0]
        return InventoryMatch((item,), "matched", "Exact canonical SKU match.", item.sku)
    if len(exact_sku) > 1:
        return InventoryMatch((), "ambiguous", "The canonical SKU maps to multiple inventory records.")

    embedded = {
        _canonical(token)
        for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]*", component)
        if _canonical(token) in by_sku
    }
    if len(embedded) == 1:
        sku = next(iter(embedded))
        matches = by_sku[sku]
        if len(matches) != 1:
            return InventoryMatch((), "ambiguous", "An embedded canonical SKU maps to multiple inventory records.")
        item = matches[0]
        return InventoryMatch((item,), "matched", "Exact canonical SKU embedded in the component description.", item.sku)
    if len(embedded) > 1:
        return InventoryMatch((), "ambiguous", "The component description contains multiple canonical SKUs.")

    exact_name = [item for item in items if _canonical(item.name) == _canonical(component)]
    if len(exact_name) == 1:
        return InventoryMatch((exact_name[0],), "matched", "Exact canonical product-name match.", exact_name[0].sku)
    if len(exact_name) > 1:
        return InventoryMatch((), "ambiguous", "The product name maps to multiple inventory records.")

    return InventoryMatch((), "missing", "No canonical SKU or product mapping exists for this component.")


def inventory_for_component(
    db: Session,
    organization_id: uuid.UUID,
    supplier_id: uuid.UUID | None,
    product_component: str,
) -> InventoryLookup:
    match = resolve_inventory_for_component(db, organization_id, supplier_id, product_component)
    status = "unmapped" if match.status == "missing" else match.status
    return InventoryLookup(status, match.items, match.reason)


def supplier_json(
    supplier: Supplier,
    metrics: SupplierMetrics | None = None,
    *,
    detail: bool = False,
    db: Session | None = None,
) -> dict:
    payload = {
        "id": str(supplier.id),
        "name": supplier.name,
        "contact_name": supplier.contact_name,
        "contact_email": supplier.contact_email,
        "contact_phone": supplier.contact_phone,
        "city": supplier.city,
        "country": supplier.country,
        "categories": supplier.categories or [],
        "promised_lead_days": supplier.promised_lead_days,
        "notes": supplier.notes,
        "status": supplier.status,
        "synthetic": supplier.synthetic,
        "created_at": iso(supplier.created_at),
        "metrics": metrics.model_dump() if metrics else None,
    }
    if detail and db is not None:
        orders = db.scalars(
            select(PurchaseOrder)
            .where(
                PurchaseOrder.organization_id == supplier.organization_id,
                PurchaseOrder.supplier_id == supplier.id,
            )
            .order_by(PurchaseOrder.order_date.desc())
        ).all()
        complaints = db.scalars(
            select(SupplierComplaint)
            .where(
                SupplierComplaint.organization_id == supplier.organization_id,
                SupplierComplaint.supplier_id == supplier.id,
            )
            .order_by(SupplierComplaint.reported_date.desc())
        ).all()
        from ..models import QualityIncident

        incidents = db.scalars(
            select(QualityIncident)
            .where(
                QualityIncident.organization_id == supplier.organization_id,
                QualityIncident.supplier_id == supplier.id,
            )
            .order_by(QualityIncident.occurred_at.desc())
        ).all()
        payload["orders"] = [order_json(o, supplier.name, metrics) for o in orders]
        payload["complaints"] = [
            {
                "id": str(c.id),
                "order_id": str(c.order_id) if c.order_id else None,
                "complaint_type": c.complaint_type,
                "severity": c.severity,
                "description": c.description,
                "reported_date": iso(c.reported_date),
                "status": c.status,
            }
            for c in complaints
        ]
        payload["quality_incidents"] = [
            {
                "id": str(i.id),
                "order_id": str(i.order_id) if i.order_id else None,
                "description": i.description,
                "severity": i.severity,
                "occurred_at": iso(i.occurred_at),
                "resolved": i.resolved,
            }
            for i in incidents
        ]
    return payload


def order_json(order: PurchaseOrder, supplier_name: str | None = None, metrics: SupplierMetrics | None = None) -> dict:
    return {
        "id": str(order.id),
        "supplier_id": str(order.supplier_id),
        "supplier_name": supplier_name,
        "order_number": order.order_number,
        "product": order.product,
        "quantity": order.quantity,
        "order_date": iso(order.order_date),
        "promised_date": iso(order.promised_date),
        "estimated_arrival": iso(order.estimated_arrival),
        "actual_arrival": iso(order.actual_arrival),
        "status": order.status,
        "priority": order.priority,
        "destination": order.destination,
        "transport_mode": order.transport_mode,
        "tracking_reference": order.tracking_reference,
        "financial_impact": order.financial_impact,
        "notes": order.notes,
        "synthetic": order.synthetic,
        "delay_days": metrics_service.delay_days(order),
        "risk_level": metrics_service.risk_level_for(order, metrics),
        "created_at": iso(order.created_at),
    }


def event_json(event: ShipmentEvent) -> dict:
    return {
        "id": str(event.id),
        "order_id": str(event.order_id),
        "event_type": event.event_type,
        "event_date": iso(event.event_date),
        "location": event.location,
        "description": event.description,
        "source": event.source,
        "synthetic": event.synthetic,
    }


def get_supplier_or_404(db: Session, organization: Organization, supplier_id: uuid.UUID) -> Supplier:
    supplier = db.get(Supplier, supplier_id)
    if supplier is None or supplier.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


def get_order_or_404(db: Session, organization: Organization, order_id: uuid.UUID) -> PurchaseOrder:
    order = db.get(PurchaseOrder, order_id)
    if order is None or order.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
