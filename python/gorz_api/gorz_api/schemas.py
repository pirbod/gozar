from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ScenarioId = Literal[
    "direct_ok",
    "relay_ok",
    "delayed",
    "degraded",
    "domestic_only",
    "blocked",
    "peer_offline",
]

Classification = Literal[
    "delivered_confirmed",
    "delivered_probable",
    "degraded_or_partial",
    "not_delivered_or_no_proof",
]


class HealthResponse(BaseModel):
    service: str = "gorz-api"
    status: str
    version: str
    safety_mode: str
    storage_backend: str
    timestamp: datetime


class IdentityCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    device_label: str = Field(min_length=1, max_length=120)


class IdentityResponse(BaseModel):
    identity_id: str
    device_id: str | None = None
    display_name: str
    device_label: str | None = None
    public_key_demo: str
    safety_notice: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ConversationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    participant_ids: list[str] = Field(min_length=1)


class ConversationSummary(BaseModel):
    conversation_id: str
    title: str
    participant_ids: list[str]
    created_at: datetime


class MessageCreate(BaseModel):
    conversation_id: str
    sender_id: str
    body: str = Field(min_length=1, max_length=4000)
    scenario: ScenarioId


class ConfidenceExplanation(BaseModel):
    top_positive_factors: list[str]
    top_negative_factors: list[str]
    human_summary: str
    recommended_user_message: str
    scenario_summary: str | None = None


class DiagnosticResponse(BaseModel):
    scenario: ScenarioId
    label: str
    dns_score: float
    transport_score: float
    tls_or_quic_score: float
    app_delivery_score: float
    path_diversity_score: float
    source_independence_score: float
    risk_penalty: float
    confidence: float
    classification: Classification
    mandatory_score: float
    support_score: float
    explanation: ConfidenceExplanation


class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    sender_id: str
    scenario: ScenarioId
    redacted_preview: str
    envelope_hash: str
    delivery_status: Classification
    confidence: float
    evidence: dict[str, Any]
    redaction_status: str
    created_at: datetime


class ConversationDetail(ConversationSummary):
    messages: list[MessageResponse]


class ScenarioInfo(BaseModel):
    id: ScenarioId
    label: str
    explanation: str


class IncidentResponse(BaseModel):
    incident_id: str
    created_at: datetime
    record: dict[str, Any]


class AuditResponse(BaseModel):
    event_id: str
    event_type: str
    actor_id: str | None
    summary: str
    metadata: dict[str, Any]
    created_at: datetime


class AuditPage(BaseModel):
    items: list[AuditResponse]
    limit: int
    offset: int
    total: int


class SafetyResponse(BaseModel):
    safety_mode: str
    pause_enabled: bool
    limitations: list[str]
    updated_at: datetime | None

