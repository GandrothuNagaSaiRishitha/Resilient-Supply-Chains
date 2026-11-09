"""Validation schemas for crisis and incident workflows."""
import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

CrisisType = Literal["Shipment Disruption", "Supplier Failure", "Inventory Shortage"]
Urgency = Literal["Low", "Medium", "High", "Critical"]
StrategyKey = Literal["wait", "reroute", "emergency-sourcing", "redistribute"]

class CrisisReportCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    crisis_type: CrisisType = Field(alias="crisisType")
    incident_title: str = Field(alias="incidentTitle", min_length=3, max_length=250)
    description: str = Field(min_length=10, max_length=8000)
    supplier_id: str = Field(alias="supplierId", min_length=1)
    shipment_id: str | None = Field(default=None, alias="shipmentId")
    product_component: str = Field(alias="productComponent", min_length=1, max_length=200)
    origin: str | None = None
    destination: str | None = None
    expected_delay_days: int | None = Field(default=None, alias="expectedDelayDays", ge=0, le=365)
    available_inventory_quantity: int | None = Field(default=None, alias="availableInventoryQuantity", ge=0)
    affected_orders: int = Field(default=0, alias="affectedOrders", ge=0)
    urgency: Urgency = "Medium"
    incident_date: datetime = Field(alias="incidentDate")

    @model_validator(mode="after")
    def validate_crisis_details(self):
        if not self.incident_title.strip():
            raise ValueError("incidentTitle must not be blank")
        if not self.description.strip():
            raise ValueError("description must not be blank")
        if not self.supplier_id.strip():
            raise ValueError("supplierId must not be blank")
        if not self.product_component.strip():
            raise ValueError("productComponent must not be blank")
        if self.crisis_type == "Shipment Disruption":
            if not self.shipment_id or not self.shipment_id.strip():
                raise ValueError("shipmentId is required for shipment disruptions")
            if not self.origin or not self.origin.strip():
                raise ValueError("origin is required for shipment disruptions")
            if not self.destination or not self.destination.strip():
                raise ValueError("destination is required for shipment disruptions")
        if self.crisis_type in {"Shipment Disruption", "Supplier Failure"} and self.expected_delay_days is None:
            raise ValueError("expectedDelayDays is required for this crisis type")
        if self.crisis_type == "Inventory Shortage" and self.available_inventory_quantity is None:
            raise ValueError("availableInventoryQuantity is required for inventory shortages")
        return self


class RecoveryConfirmationCreate(BaseModel):
    incident_id: uuid.UUID = Field(alias="incidentId")
    strategy_key: StrategyKey = Field(alias="strategyKey")


class DecisionActionCreate(BaseModel):
    incident_id: uuid.UUID = Field(alias="incidentId")
    request_id: uuid.UUID | None = Field(default=None, alias="requestId")
    action: Literal["accepted", "rejected", "alternative"]
    strategy_key: StrategyKey | None = Field(alias="strategyKey")
    explanation: str = Field(default="", max_length=4000)

    @model_validator(mode="after")
    def validate_strategy(self):
        if self.action == "rejected" and self.strategy_key is not None:
            raise ValueError("Rejected actions must have a null strategyKey")
        if self.action != "rejected" and self.strategy_key is None:
            raise ValueError("A strategyKey is required unless the recommendation is rejected")
        return self


class OutcomeFeedbackCreate(BaseModel):
    incident_id: uuid.UUID = Field(alias="incidentId")
    strategy_key: StrategyKey = Field(alias="strategyKey")
    actual_additional_cost: float = Field(alias="actualAdditionalCost", ge=0)
    actual_delivery_delay_days: int = Field(alias="actualDeliveryDelayDays", ge=0)
    actual_inventory_shortage: int = Field(alias="actualInventoryShortage", ge=0)
    orders_affected: int = Field(alias="ordersAffected", ge=0)
    successful: bool
    lessons_learned: str = Field(default="", alias="lessonsLearned", max_length=8000)
    additional_notes: str = Field(default="", alias="additionalNotes", max_length=8000)

class IncidentStatusUpdate(BaseModel):
    status: Literal["open", "investigating", "mitigating", "resolved"]
