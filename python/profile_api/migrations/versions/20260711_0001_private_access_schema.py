"""Create durable private-access profile schema.

Revision ID: 20260711_0001
Revises:
Create Date: 2026-07-11
"""

import sqlalchemy as sa
from alembic import op

revision = "20260711_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("device_id", sa.String(length=48), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("platform", sa.String(length=24), nullable=False),
        sa.Column("app_version", sa.String(length=40), nullable=False),
        sa.Column("device_public_key", sa.Text(), nullable=False),
        sa.Column("device_public_key_hash", sa.String(length=80), nullable=False),
        sa.Column("capabilities_json", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=24), server_default="active", nullable=False),
        sa.Column("auth_token_hash", sa.String(length=80), nullable=True),
        sa.Column("wireguard_public_key", sa.Text(), nullable=True),
        sa.Column("assigned_address", sa.String(length=48), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("device_id"),
        sa.UniqueConstraint("assigned_address"),
        sa.UniqueConstraint("auth_token_hash"),
        sa.UniqueConstraint("device_public_key_hash"),
        sa.UniqueConstraint("wireguard_public_key"),
    )
    op.create_index("ix_devices_auth_token_hash", "devices", ["auth_token_hash"])
    op.create_index("ix_devices_device_public_key_hash", "devices", ["device_public_key_hash"])
    op.create_index("ix_devices_status", "devices", ["status"])

    op.create_table(
        "session_profiles",
        sa.Column("profile_id", sa.String(length=48), nullable=False),
        sa.Column("device_id_hash", sa.String(length=80), nullable=False),
        sa.Column("audience_hash", sa.String(length=80), nullable=False),
        sa.Column("profile_type", sa.String(length=48), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ttl_seconds", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("policy_version", sa.String(length=48), nullable=False),
        sa.Column("redacted_routing_mode", sa.String(length=48), nullable=False),
        sa.Column("safety_notes_json", sa.Text(), nullable=False),
        sa.Column("signed_envelope_json", sa.Text(), nullable=False),
        sa.Column("signature", sa.Text(), nullable=False),
        sa.Column("issuer_key_id", sa.String(length=48), nullable=False),
        sa.Column("issuer_public_key", sa.Text(), nullable=False),
        sa.Column("envelope_hash", sa.String(length=80), nullable=False),
        sa.Column("encrypted_payload_hash", sa.String(length=80), nullable=False),
        sa.Column("signature_hash", sa.String(length=80), nullable=False),
        sa.Column("signature_format_valid", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("profile_id"),
    )
    op.create_index("ix_session_profiles_audience_hash", "session_profiles", ["audience_hash"])
    op.create_index("ix_session_profiles_device_id_hash", "session_profiles", ["device_id_hash"])
    op.create_index("ix_session_profiles_issuer_key_id", "session_profiles", ["issuer_key_id"])

    op.create_table(
        "revoked_profiles",
        sa.Column("profile_id", sa.String(length=48), nullable=False),
        sa.Column("reason", sa.String(length=48), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("profile_id"),
    )
    op.create_table(
        "audit_events",
        sa.Column("event_id", sa.String(length=48), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("actor_id_hash", sa.String(length=80), nullable=True),
        sa.Column("summary", sa.String(length=260), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_table(
        "safety_state",
        sa.Column("state_id", sa.String(length=32), nullable=False),
        sa.Column("pause_enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("state_id"),
    )
    op.create_table(
        "issuer_keys",
        sa.Column("key_id", sa.String(length=48), nullable=False),
        sa.Column("public_key", sa.Text(), nullable=False),
        sa.Column("private_key_demo", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("rotation_reason", sa.String(length=80), nullable=True),
        sa.Column("created_by", sa.String(length=40), nullable=False),
        sa.Column("safety_note", sa.String(length=180), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("key_id"),
    )


def downgrade() -> None:
    op.drop_table("issuer_keys")
    op.drop_table("safety_state")
    op.drop_table("audit_events")
    op.drop_table("revoked_profiles")
    op.drop_index("ix_session_profiles_issuer_key_id", table_name="session_profiles")
    op.drop_index("ix_session_profiles_device_id_hash", table_name="session_profiles")
    op.drop_index("ix_session_profiles_audience_hash", table_name="session_profiles")
    op.drop_table("session_profiles")
    op.drop_index("ix_devices_status", table_name="devices")
    op.drop_index("ix_devices_device_public_key_hash", table_name="devices")
    op.drop_index("ix_devices_auth_token_hash", table_name="devices")
    op.drop_table("devices")
