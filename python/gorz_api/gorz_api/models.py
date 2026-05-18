from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


class Base(DeclarativeBase):
    pass


class Identity(Base):
    __tablename__ = "identities"

    identity_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    public_key_demo: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)


class Device(Base):
    __tablename__ = "devices"

    device_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    identity_id: Mapped[str] = mapped_column(ForeignKey("identities.identity_id"), nullable=False)
    device_label: Mapped[str] = mapped_column(String(120), nullable=False)
    public_key_demo: Mapped[str] = mapped_column(Text, nullable=False)
    private_key_demo_for_tests: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)


class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.conversation_id"), primary_key=True
    )
    identity_id: Mapped[str] = mapped_column(ForeignKey("identities.identity_id"), primary_key=True)


class Message(Base):
    __tablename__ = "messages"

    message_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.conversation_id"), nullable=False
    )
    sender_id: Mapped[str] = mapped_column(ForeignKey("identities.identity_id"), nullable=False)
    scenario: Mapped[str] = mapped_column(String(40), nullable=False)
    redacted_preview: Mapped[str] = mapped_column(String(160), nullable=False)
    ciphertext_demo: Mapped[str] = mapped_column(Text, nullable=False)
    envelope_hash: Mapped[str] = mapped_column(String(80), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(48), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    redaction_status: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)


class MessageEvidence(Base):
    __tablename__ = "message_evidence"

    evidence_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.message_id"), nullable=False)
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)


class Incident(Base):
    __tablename__ = "incidents"

    incident_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.message_id"), nullable=False)
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.conversation_id"), nullable=False
    )
    record_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(48), nullable=True)
    summary: Mapped[str] = mapped_column(String(260), nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)


class SafetyState(Base):
    __tablename__ = "safety_state"

    state_id: Mapped[str] = mapped_column(String(32), primary_key=True, default="singleton")
    pause_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
