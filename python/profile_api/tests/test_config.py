from __future__ import annotations

import pytest

from profile_api.config import Settings
from profile_api.main import create_app


def test_local_only_allows_demo_private_keys(tmp_path) -> None:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'local.sqlite3'}",
        safety_mode="local_only",
        allow_demo_private_keys=True,
    )

    app = create_app(settings)

    assert app.state.settings.safety_mode == "local_only"


def test_non_local_mode_rejects_demo_private_keys(tmp_path) -> None:
    with pytest.raises(ValueError, match="PROFILE_ALLOW_DEMO_PRIVATE_KEYS"):
        Settings(
            database_url=f"sqlite:///{tmp_path / 'non-local.sqlite3'}",
            safety_mode="shared_lab",
            allow_demo_private_keys=True,
        )


def test_invalid_audit_timestamp_bucket_fails() -> None:
    with pytest.raises(ValueError, match="PROFILE_AUDIT_TIMESTAMP_BUCKET_MINUTES"):
        Settings(audit_timestamp_bucket_minutes=45)

def test_staging_requires_postgresql() -> None:
    with pytest.raises(ValueError, match="PostgreSQL"):
        Settings(
            environment="staging",
            enable_demo_api=False,
            allow_demo_private_keys=False,
            database_url="sqlite:///staging.sqlite3",
            admin_token="admin-" + "a" * 40,
            enrollment_token="enroll-" + "b" * 40,
            device_token_pepper="pepper-" + "c" * 40,
            issuer_private_key="IiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiI=",
        )


def test_staging_accepts_explicit_production_dependencies() -> None:
    settings = Settings(
        environment="staging",
        enable_demo_api=False,
        allow_demo_private_keys=False,
        database_url="postgresql+psycopg://gozar:secret@postgres/gozar",
        admin_token="admin-" + "a" * 40,
        enrollment_token="enroll-" + "b" * 40,
        device_token_pepper="pepper-" + "c" * 40,
        issuer_private_key="IiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiI=",
    )

    assert settings.storage_backend == "postgresql"


def test_public_route_is_rejected() -> None:
    with pytest.raises(ValueError, match="non-private route"):
        Settings(approved_routes=["0.0.0.0/0"])
