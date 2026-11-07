import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

ORDER_STATUSES = [
    "created",
    "confirmed",
    "processing",
    "dispatched",
    "in_transit",
    "delayed",
    "delivered",
    "cancelled",
]
PRIORITIES = ["low", "normal", "high", "critical"]
SOURCE_TYPES = [
    "verified_business_fact",
    "user_reported_fact",
    "imported_external_observation",
    "ai_inference",
    "recommendation",
]
MEMORY_CATEGORIES = ["episodic", "semantic", "decision", "outcome", "preference", "future_action"]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- auth ----------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=200)
    organization_name: str = Field(min_length=2, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(ORMModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    organization_id: uuid.UUID


class OrganizationOut(ORMModel):
    id: uuid.UUID
    name: str
    slug: str
    is_demo: bool


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    organization: OrganizationOut


class MeResponse(BaseModel):
    user: UserOut
    organization: OrganizationOut


# ---------- suppliers ----------
class SupplierBase(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    categories: list[str] = Field(default_factory=list)
    promised_lead_days: int = Field(default=7, ge=1, le=180)
    notes: Optional[str] = None
    status: str = "active"


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    categories: Optional[list[str]] = None
    promised_lead_days: Optional[int] = Field(default=None, ge=1, le=180)
    notes: Optional[str] = None
    status: Optional[str] = None


class SupplierMetrics(BaseModel):
    delivered_orders: int = 0
    avg_delay_days: float = 0.0
    max_delay_days: float = 0.0
    on_time_rate: float = 0.0
    reliability_score: float = 0.0
    quality_complaints: int = 0
    communication_complaints: int = 0
    transportation_incidents: int = 0
    open_orders: int = 0
    late_open_orders: int = 0


class SupplierOut(ORMModel):
    id: uuid.UUID
    name: str
    contact_name: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    city: Optional[str]
    country: Optional[str]
    categories: list
    promised_lead_days: int
    notes: Optional[str]
    status: str
    synthetic: bool
    created_at: datetime
    metrics: Optional[SupplierMetrics] = None


# ---------- orders ----------
class OrderBase(BaseModel):
    supplier_id: uuid.UUID
    order_number: Optional[str] = None
    product: str = Field(min_length=1, max_length=200)
    quantity: int = Field(gt=0)
    order_date: Optional[datetime] = None
    promised_date: datetime
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    status: Literal[
        "created", "confirmed", "processing", "dispatched", "in_transit", "delayed", "delivered", "cancelled"
    ] = "created"
    priority: Literal["low", "normal", "high", "critical"] = "normal"
    destination: Optional[str] = None
    transport_mode: Literal["road", "rail", "air", "sea", "multimodal"] = "road"
    tracking_reference: Optional[str] = None
    financial_impact: float = Field(default=0.0, ge=0)
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    supplier_id: Optional[uuid.UUID] = None
    product: Optional[str] = None
    quantity: Optional[int] = Field(default=None, gt=0)
    promised_date: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    status: Optional[Literal[
        "created", "confirmed", "processing", "dispatched", "in_transit", "delayed", "delivered", "cancelled"
    ]] = None
    priority: Optional[Literal["low", "normal", "high", "critical"]] = None
    destination: Optional[str] = None
    transport_mode: Optional[Literal["road", "rail", "air", "sea", "multimodal"]] = None
    tracking_reference: Optional[str] = None
    financial_impact: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = None


class OrderOut(ORMModel):
    id: uuid.UUID
    supplier_id: uuid.UUID
    supplier_name: Optional[str] = None
    order_number: str
    product: str
    quantity: int
    order_date: datetime
    promised_date: datetime
    estimated_arrival: Optional[datetime]
    actual_arrival: Optional[datetime]
    status: str
    priority: str
    destination: Optional[str]
    transport_mode: str
    tracking_reference: Optional[str]
    financial_impact: float
    notes: Optional[str]
    synthetic: bool
    delay_days: Optional[float] = None
    risk_level: Optional[str] = None
    created_at: datetime


class ShipmentEventCreate(BaseModel):
    event_type: str = Field(min_length=2, max_length=50)
    event_date: Optional[datetime] = None
    location: Optional[str] = None
    description: str = Field(min_length=2)
    source: str = "manual"


class ShipmentEventOut(ORMModel):
    id: uuid.UUID
    order_id: uuid.UUID
    event_type: str
    event_date: datetime
    location: Optional[str]
    description: str
    source: str
    synthetic: bool


# ---------- memory ----------
class MemoryRetainRequest(BaseModel):
    content: str = Field(min_length=3, max_length=8000)
    category: Literal["episodic", "semantic", "decision", "outcome", "preference", "future_action"] = "episodic"
    context: Optional[str] = None
    source_type: Literal[
        "verified_business_fact",
        "user_reported_fact",
        "imported_external_observation",
        "ai_inference",
        "recommendation",
    ] = "user_reported_fact"
    supplier_id: Optional[uuid.UUID] = None
    order_id: Optional[uuid.UUID] = None
    event_date: Optional[datetime] = None
    confidence: float = Field(default=0.8, ge=0, le=1)
    document_id: Optional[str] = None


class MemoryRecallRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    types: Optional[list[str]] = None
    max_tokens: int = Field(default=4096, ge=256, le=32000)
    budget: Literal["low", "mid", "high"] = "mid"


class MemoryReflectRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    context: Optional[str] = None
    budget: Literal["low", "mid", "high"] = "mid"


class MemoryHit(BaseModel):
    id: Optional[str] = None
    text: str
    type: Optional[str] = None
    score: Optional[float] = None
    metadata: dict = Field(default_factory=dict)


class MemoryOperationOut(BaseModel):
    operation: str
    status: str
    bank_id: str
    result_count: int = 0
    latency_ms: int = 0
    results: list[MemoryHit] = Field(default_factory=list)
    text: Optional[str] = None
    operation_id: Optional[str] = None


# ---------- agent ----------
class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=4000)
    conversation_id: Optional[uuid.UUID] = None
    memory_enabled: bool = True
    new_conversation: bool = False


class ToolCallTrace(BaseModel):
    name: str
    arguments: dict = Field(default_factory=dict)
    result_summary: Optional[str] = None
    ok: bool = True
    duration_ms: Optional[int] = None


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    run_id: uuid.UUID
    answer: str
    memory_enabled: bool
    memory_hits: list[MemoryHit] = Field(default_factory=list)
    reflect_answer: Optional[str] = None
    tool_calls: list[ToolCallTrace] = Field(default_factory=list)
    evidence: dict = Field(default_factory=dict)
    model: Optional[str] = None
    duration_ms: int = 0


class AgentRunOut(ORMModel):
    id: uuid.UUID
    conversation_id: Optional[uuid.UUID]
    agent: str
    question: str
    answer: Optional[str]
    status: str
    memory_enabled: bool
    tool_calls: list
    evidence: dict
    model: Optional[str]
    duration_ms: Optional[int]
    created_at: datetime


# ---------- lab ----------
class LabSeedRequest(BaseModel):
    reset_first: bool = False


class LabRunRequest(BaseModel):
    question: Optional[str] = None
    stages: list[int] = Field(default_factory=lambda: [0, 1, 5, 10, 20])


class LabStageRequest(BaseModel):
    stage: int = Field(ge=0, le=20)
    experiment_id: Optional[str] = Field(default=None, max_length=64)
    force: bool = False


class LabResetRequest(BaseModel):
    confirm: bool = False


# ---------- alerts ----------
class AlertOut(ORMModel):
    id: uuid.UUID
    order_id: Optional[uuid.UUID]
    supplier_id: Optional[uuid.UUID]
    alert_type: str
    severity: str
    title: str
    message: str
    status: str
    due_at: Optional[datetime]
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]


class AlertUpdate(BaseModel):
    status: Literal["open", "acknowledged", "resolved", "dismissed"]


# ---------- what-if ----------
class WhatIfRequest(BaseModel):
    supplier_id: uuid.UUID
    disruption_days: int = Field(ge=1, le=120)
    question: Optional[str] = None


class SupplierComparisonOut(BaseModel):
    suppliers: list[dict]
    recommended_supplier_id: Optional[uuid.UUID] = None
    rationale: str
