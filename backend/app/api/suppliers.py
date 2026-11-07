"""Supplier CRUD with deterministic metrics."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import CurrentContext, audit, get_current_context
from ..models import Supplier
from ..schemas import SupplierCreate, SupplierUpdate
from ..services import metrics as metrics_service
from .common import get_supplier_or_404, supplier_json, supplier_metrics

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("")
def list_suppliers(
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    suppliers = db.scalars(
        select(Supplier)
        .where(Supplier.organization_id == ctx.organization.id)
        .order_by(Supplier.name)
    ).all()
    metrics = supplier_metrics(db, ctx.organization.id)
    rows = [supplier_json(s, metrics.get(s.id)) for s in suppliers]
    rows.sort(key=lambda r: (r["metrics"] or {}).get("reliability_score", 0), reverse=True)
    return {"count": len(rows), "suppliers": rows, "synthetic_demo_data": True}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_supplier(
    payload: SupplierCreate,
    request: Request,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    existing = db.scalar(
        select(Supplier).where(
            Supplier.organization_id == ctx.organization.id,
            Supplier.name.ilike(payload.name.strip()),
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="A supplier with this name already exists")
    supplier = Supplier(
        organization_id=ctx.organization.id,
        **payload.model_dump(exclude={"contact_email"}),
        contact_email=str(payload.contact_email) if payload.contact_email else None,
        synthetic=False,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    audit(
        db,
        ctx.organization.id,
        ctx.user.id,
        "supplier.create",
        "supplier",
        str(supplier.id),
        {"name": supplier.name},
        request.client.host if request.client else None,
    )
    db.commit()
    metrics = metrics_service.supplier_metrics_map(db, ctx.organization.id)
    return supplier_json(supplier, metrics.get(supplier.id))


@router.get("/{supplier_id}")
def get_supplier(
    supplier_id: uuid.UUID,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    supplier = get_supplier_or_404(db, ctx.organization, supplier_id)
    metrics = metrics_service.supplier_metrics_map(db, ctx.organization.id)
    return supplier_json(supplier, metrics.get(supplier.id), detail=True, db=db)


@router.patch("/{supplier_id}")
def update_supplier(
    supplier_id: uuid.UUID,
    payload: SupplierUpdate,
    ctx: CurrentContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> dict:
    supplier = get_supplier_or_404(db, ctx.organization, supplier_id)
    changes = payload.model_dump(exclude_unset=True)
    if "contact_email" in changes and changes["contact_email"]:
        changes["contact_email"] = str(changes["contact_email"])
    for key, value in changes.items():
        setattr(supplier, key, value)
    db.commit()
    db.refresh(supplier)
    metrics = metrics_service.supplier_metrics_map(db, ctx.organization.id)
    return supplier_json(supplier, metrics.get(supplier.id))
