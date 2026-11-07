from __future__ import annotations
from fastapi import APIRouter, Depends
from ..deps import get_current_context, CurrentContext
router = APIRouter(prefix="/crises", tags=["crises"])

@router.get("/form-options")
def form_options(ctx: CurrentContext = Depends(get_current_context)):
    return {"data": {"crisisTypes": ["Shipment Disruption","Supplier Failure","Inventory Shortage"],
                    "urgencyLevels": ["Low","Medium","High","Critical"]}}
