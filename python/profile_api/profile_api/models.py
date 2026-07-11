from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


class Base(DeclarativeBase):
    pass


class Device(Base):
    __tablename__ = "devices"

    device_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    platform: Mapped[str] = mapped_column(String(24), nullable=False)
    app_version: Mapped[str] = mapped_column(String(40), nullable=False)
    device_public_key: Mapped[str] = mapped_column(Text, nullable=False)
    device_public_key_hash: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    capabilities_json: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="active", nullable=False, index=True)
    auth_token_hash: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True, index=True)
    wireguard_public_key: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    assigned_address: Mapped[str | None] = mapped_column(String(48), nullable=True, unique=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class SessionProfile(Base):
    __tablename__ = "session_profiles"

    profile_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    device_id_hash: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    audience_hash: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    profile_type: Mapped[str] = mapped_column(String(48), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ttl_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="active", nullable=False)
    policy_version: Mapped[str] = mapped_column(String(48), nullable=False)
    redacted_routing_mode: Mapped[str] = mapped_column(String(48), nullable=False)
    safety_notes_json: Mapped[str] = mapped_column(Text, nullable=False)
    signed_envelope_json: Mapped[str] = mapped_column(Text, nullable=False)
    signature: Mapped[str] = mapped_column(Text, nullable=False)
    issuer_key_id: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    issuer_public_key: Mapped[str] = mapped_column(Text, nullable=False)
    envelope_hash: Mapped[str] = mapped_column(String(80), nullable=False)
    encrypted_payload_hash: Mapped[str] = mapped_column(String(80), nullable=False)
    signature_hash: Mapped[str] = mapped_column(String(80), nullable=False)
    signature_format_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class RevokedProfile(Base):
    __tablename__ = "revoked_profiles"

    profile_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    reason: Mapped[str] = mapped_column(String(48), nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    actor_id_hash: Mapped[str | None] = mapped_column(String(80), nullable=True)
    summary: Mapped[str] = mapped_column(String(260), nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class SafetyState(Base):
    __tablename__ = "safety_state"

    state_id: Mapped[str] = mapped_column(String(32), primary_key=True, default="singleton")
    pause_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class IssuerKey(Base):
    __tablename__ = "issuer_keys"

    key_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    public_key: Mapped[str] = mapped_column(Text, nullable=False)
    private_key_demo: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rotation_reason: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_by: Mapped[str] = mapped_column(String(40), default="local-demo", nullable=False)
    safety_note: Mapped[str] = mapped_column(
        String(180),
        default="Local demo signing key only. Production requires KMS/HSM-backed signing.",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
