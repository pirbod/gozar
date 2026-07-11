from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Platform = Literal["macos", "linux", "windows", "android", "ios", "unknown"]
RequestedMode = Literal["demo_full_tunnel", "demo_split_tunnel", "demo_messaging_only"]
RiskTolerance = Literal["low", "medium"]
PreviousFailureClass = Literal["none", "timeout", "blocked", "blocked_local", "degraded"]
NetworkType = Literal["wifi", "mobile", "unknown"]
ProfileType = Literal["wireguard_like_demo", "quic_like_demo", "no_profile"]
ProfileStatus = Literal["active", "expired", "revoked", "invalid_signature", "unknown"]
EnvelopeMode = Literal["sealed_box", "android_local_demo"]
RevokeReason = Literal["demo_rotation", "manual_test", "safety_pause", "compromised_demo"]
DiagnosticScenario = Literal[
    "healthy",
    "degraded",
    "blocked_local",
    "expired_profile",
    "revoked_profile",
    "safety_pause",
]


class HealthResponse(BaseModel):
    status: str
    service: str = "profile-api"
    version: str
    mode: str = "local-demo"
    safety_mode: str
    storage_backend: str
    timestamp: datetime


class DeviceCapabilities(BaseModel):
    supports_wireguard_like: bool = False
    supports_quic_like: bool = False
    supports_split_tunnel_demo: bool = False


class DeviceRegisterRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    platform: Platform = "unknown"
    app_version: str = Field(min_length=1, max_length=40)
    device_public_key: str
    capabilities: DeviceCapabilities = Field(default_factory=DeviceCapabilities)


class DeviceRegisterResponse(BaseModel):
    device_id: str
    device_public_key_hash: str
    registration_status: Literal["registered", "already_registered"]
    safety_notice: str


class DeviceResponse(BaseModel):
    device_id: str
    display_name: str
    platform: Platform
    app_version: str
    device_public_key_hash: str
    capabilities: DeviceCapabilities
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientContext(BaseModel):
    network_type: NetworkType = "unknown"
    region_hint: str = "local-demo"
    previous_failure_class: PreviousFailureClass = "none"


class SessionProfileRequest(BaseModel):
    device_id: str
    requested_mode: RequestedMode
    risk_tolerance: RiskTolerance
    client_context: ClientContext = Field(default_factory=ClientContext)
    ttl_seconds: int | None = Field(default=None, ge=1, le=900)
    envelope_mode: EnvelopeMode = "sealed_box"


class SessionProfileEnvelope(BaseModel):
    profile_id: str
    profile_type: Literal["wireguard_like_demo", "quic_like_demo"]
    envelope_mode: EnvelopeMode = "sealed_box"
    issued_at: datetime
    expires_at: datetime
    ttl_seconds: int
    audience: str
    policy_version: str
    encrypted_payload: str
    issuer_key_id: str
    signature: str
    issuer_public_key: str
    safety_notes: list[str]


class SessionProfileMetadata(BaseModel):
    profile_id: str
    device_id_hash: str
    profile_type: str
    issued_at: datetime
    expires_at: datetime
    status: ProfileStatus
    policy_version: str
    redacted_routing_mode: str
    safety_notes: list[str]


class ProfileValidationResponse(BaseModel):
    profile_id: str
    valid: bool
    status: ProfileStatus
    checks: dict[str, Literal["pass", "fail"]]


class RevokeProfileRequest(BaseModel):
    reason: RevokeReason


class RevokeProfileResponse(BaseModel):
    profile_id: str
    status: Literal["revoked"]
    revoked_at: datetime
    reason: RevokeReason


class DiagnosticRequest(BaseModel):
    scenario: DiagnosticScenario


class DiagnosticResponse(BaseModel):
    scenario: DiagnosticScenario
    profile_recommendation: ProfileType
    confidence: float = Field(ge=0.0, le=1.0)
    risk: Literal["low", "medium", "high"]
    explanation: str
    safety_notes: list[str]


class AuditEntry(BaseModel):
    event_id: str
    event_type: str
    actor_id_hash: str | None
    summary: str
    metadata: dict[str, Any]
    created_at: datetime


class AuditPage(BaseModel):
    items: list[AuditEntry]
    limit: int
    offset: int
    total: int


class AuditExportBundle(BaseModel):
    bundle_id: str
    created_at: datetime
    scope: str
    timestamp_bucket_minutes: int
    entries: list[dict[str, Any]]
    redaction: dict[str, bool]
    safety_notes: list[str]


class SafetyResponse(BaseModel):
    local_only: bool
    public_network_probing: bool
    os_vpn_installation: bool
    production_vpn: bool
    relay_discovery: bool
    external_gateway: bool
    pause_enabled: bool
    limitations: list[str]
    updated_at: datetime | None


class IssuerRotateRequest(BaseModel):
    reason: Literal["manual_test", "demo_rotation"]


class IssuerRotateResponse(BaseModel):
    old_key_id: str | None
    new_key_id: str
    active: bool
    safety_note: str


class MobileBootstrapResponse(BaseModel):
    service: str
    mode: str
    issuer_public_key: str
    default_ttl_seconds: int
    supported_profile_types: list[Literal["wireguard_like_demo", "quic_like_demo"]]
    android_emulator_api_url_hint: str
    safety_notes: list[str]

class PrivateAccessEnrollmentRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    app_version: str = Field(min_length=1, max_length=40)
    device_public_key: str = Field(min_length=44, max_length=44)
    wireguard_public_key: str = Field(min_length=44, max_length=44)


class PrivateAccessEnrollmentResponse(BaseModel):
    device_id: str
    device_token: str
    assigned_address: str
    status: Literal["active"]
    token_type: Literal["Bearer"] = "Bearer"


class PrivateAccessDeviceResponse(BaseModel):
    device_id: str
    display_name: str
    status: str
    assigned_address: str
    approved_routes: list[str]
    last_seen_at: datetime | None


class PrivateAccessProfileRequest(BaseModel):
    ttl_seconds: int | None = Field(default=None, ge=60, le=3600)


class PrivateAccessService(BaseModel):
    id: str
    name: str
    host: str
    port: int
    protocol: Literal["http", "https", "tcp"]


class PrivateAccessProfileEnvelope(BaseModel):
    profile_id: str
    device_id: str
    audience: str
    issued_at: datetime
    expires_at: datetime
    ttl_seconds: int
    client_address: str
    gateway_public_key: str
    gateway_endpoint: str
    approved_routes: list[str]
    approved_services: list[PrivateAccessService]
    dns_servers: list[str]
    persistent_keepalive_seconds: int = 25
    policy_version: str
    issuer_key_id: str
    issuer_public_key: str
    signature: str
