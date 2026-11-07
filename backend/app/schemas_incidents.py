"""Validation schemas for crisis and incident workflows."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

CrisisType = Literal["Shipment Disruption", "Supplier Failure", "Inventory Shortage"]
Urgency = Literal["Low", "Medium", "High", "Critical"]

class CrisisReportCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    crisis_type: CrisisType = Field(alias="crisisType")
    incident_title: str = Field(alias="incidentTitle", min_length=3, max_length=250)
    description: str = Field(min_length=10, max_length=8000)
    supplier_id: str | None = Field(default=None, alias="supplierId")
    shipment_id: str | None = Field(default=None, alias="shipmentId")
    product_component: str = Field(alias="productComponent", min_length=1, max_length=200)
    origin: str | None = None
    destination: str | None = None
    expected_delay_days: int | None = Field(default=None, alias="expectedDelayDays", ge=0, le=365)
    available_inventory_quantity: int | None = Field(default=None, alias="availableInventoryQuantity", ge=0)
    affected_orders: int = Field(default=0, alias="affectedOrders", ge=0)
    urgency: Urgency = "Medium"
    incident_date: datetime = Field(alias="incidentDate")

class IncidentStatusUpdate(BaseModel):
    status: Literal["open", "investigating", "mitigating", "resolved"]
