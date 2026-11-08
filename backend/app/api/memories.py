from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import get_current_context, CurrentContext
from ..services import memory as memory_service
from ..schemas_incidents import CrisisType

router = APIRouter(prefix="/memories", tags=["memories"])

def _historical_memory(record: dict) -> dict | None:
    metadata = record.get("metadata") or {}
    crisis_type = metadata.get("crisis_type")
    successful = metadata.get("successful")
    if crisis_type not in {"Shipment Disruption", "Supplier Failure", "Inventory Shortage"}:
        return None
    if successful not in {True, False, "true", "false", "True", "False"}:
        return None
    content = record["content"]
    event_date = record.get("event_date") or record.get("created_at")
    supplier = record.get("supplier") or "Unassigned"
    success = successful is True or str(successful).lower() == "true"
    strategy = metadata.get("strategy_key") or "Not recorded"
    return {
        "id": record["id"],
        "incidentDate": event_date[:10] if event_date else "",
        "crisisType": crisis_type,
        "supplier": supplier,
        "title": metadata.get("incident_title") or content[:100],
        "description": content,
        "decisionTaken": strategy,
        "expectedResult": metadata.get("expected_result") or "Not recorded",
        "actualOutcome": content,
        "outcome": "Successful" if success else "Ineffective",
        "lessonLearned": metadata.get("lessons_learned") or content,
        "demoRecord": bool(record.get("synthetic")),
    }

def _memories(db: Session, ctx: CurrentContext, query: str) -> list[dict]:
    records = memory_service.records(db, ctx.organization, limit=1000)
    by_document = {record.get("document_id"): record for record in records if record.get("document_id")}
    try:
        recalled = memory_service.recall(
            db,
            ctx.organization,
            query=query,
            max_tokens=16000,
            budget="low",
        )
    except memory_service.HindsightUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail="Hindsight memory retrieval is unavailable. Check the Hindsight service and try again.",
        ) from exc
    memories = []
    for hit in recalled["results"]:
        provenance = hit.get("provenance") or {}
        record = by_document.get(hit.get("document_id"))
        memory = _historical_memory({
            "id": (record or {}).get("id") or hit.get("document_id") or hit.get("id"),
            "metadata": (record or {}).get("metadata") or hit.get("metadata") or {},
            "content": hit.get("text", ""),
            "event_date": provenance.get("event_date") or hit.get("occurred_start"),
            "supplier": (record or {}).get("supplier"),
            "synthetic": (record or {}).get("synthetic", False),
        })
        if memory:
            memories.append(memory)
    return memories

@router.get("/overview")
def overview(ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db)):
    memories = _memories(
        db,
        ctx,
        "historical supply chain crisis incident recovery outcome decision lessons",
    )
    successful = sum(memory["outcome"] == "Successful" for memory in memories)
    return {"data": {
        "stats": {
            "totalHistoricalIncidents": len(memories),
            "successfulStrategies": successful,
            "ineffectiveStrategies": len(memories) - successful,
            "lessonsRetained": sum(bool(memory["lessonLearned"]) for memory in memories),
        },
        "memories": memories,
        "insights": [],
        "lifecycle": [
            {"id": "retain", "title": "Retain", "description": "Record incident outcomes in Hindsight organizational memory.", "example": "Incident outcome saved to the organization bank."},
            {"id": "recall", "title": "Recall", "description": "Retrieve relevant retained experiences for a new decision.", "example": "Recommendation and replay requests recall Hindsight memories."},
            {"id": "reflect", "title": "Reflect", "description": "Synthesize patterns from retained organizational experiences.", "example": "Reflection is available through the existing memory API."},
        ],
        "crisisTypes": sorted({memory["crisisType"] for memory in memories}),
        "suppliers": sorted({memory["supplier"] for memory in memories if memory["supplier"] != "Unassigned"}),
    }}

@router.get("")
def search(ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db),
           crisisType: CrisisType | None = Query(None), supplier: str = Query(""), outcome: str = Query(""),
           dateFrom: date | None = Query(None), dateTo: date | None = Query(None)):
    if outcome and outcome not in {"Successful", "Ineffective"}:
        raise HTTPException(status_code=422, detail="outcome must be Successful or Ineffective")
    if dateFrom and dateTo and dateFrom > dateTo:
        raise HTTPException(status_code=422, detail="dateFrom must not be after dateTo")
    terms = ["historical supply chain incident outcomes lessons"]
    if crisisType:
        terms.append(crisisType)
    if supplier:
        terms.append(supplier)
    if outcome:
        terms.append(outcome)
    if dateFrom:
        terms.append(f"since {dateFrom.isoformat()}")
    if dateTo:
        terms.append(f"through {dateTo.isoformat()}")
    memories = _memories(db, ctx, " ".join(terms))
    filtered = [
        memory for memory in memories
        if (not crisisType or memory["crisisType"] == crisisType)
        and (not supplier or memory["supplier"] == supplier)
        and (not outcome or memory["outcome"] == outcome)
        and (not dateFrom or memory["incidentDate"] >= dateFrom.isoformat())
        and (not dateTo or memory["incidentDate"] <= dateTo.isoformat())
    ]
    return {"data": filtered}

@router.get("/{memoryId}")
def detail(memoryId: str, ctx: CurrentContext = Depends(get_current_context), db: Session = Depends(get_db)):
    record = next(
        (item for item in memory_service.records(db, ctx.organization, limit=1000) if item["id"] == memoryId),
        None,
    )
    if record:
        memories = _memories(
            db,
            ctx,
            record["content"],
        )
        for memory in memories:
            if memory["id"] == memoryId:
                return {"data": memory}
    raise HTTPException(status_code=404, detail="Memory not found")
