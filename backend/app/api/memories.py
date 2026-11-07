from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import get_current_context, CurrentContext
from ..services import memory as memory_service

router = APIRouter(prefix="/memories", tags=["memories"])

@router.get("/overview")
def overview(ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db)):
    o = memory_service.overview(db, ctx.organization)
    records = memory_service.records(db, ctx.organization)
    suppliers = sorted({r.get("supplier") for r in records if r.get("supplier")})
    crisis_types = sorted({r.get("category") for r in records})
    return {"data": {"stats": o, "memories": records, "insights": [], "lifecycle": {}, "crisisTypes": crisis_types, "suppliers": suppliers}}

@router.get("")
def search(ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db),
           crisisType: str = Query(""), supplier: str = Query(""), outcome: str = Query(""),
           dateFrom: str = Query(""), dateTo: str = Query("")):
    recs = memory_service.records(db, ctx.organization)
    filtered = [r for r in recs if (not crisisType or r.get("category")==crisisType)
                and (not supplier or r.get("supplier")==supplier)
                and (not dateFrom or (r.get("event_date") or "") >= dateFrom)
                and (not dateTo or (r.get("event_date") or "") <= dateTo)]
    return {"data": filtered}

@router.get("/{memoryId}")
def detail(memoryId: str, ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db)):
    recs = memory_service.records(db, ctx.organization)
    for r in recs:
        if r.get("id") == memoryId or r.get("document_id") == memoryId:
            return {"data": r}
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Memory not found")
