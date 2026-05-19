from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

SUPPORTED_AUDIT_TIMESTAMP_BUCKET_MINUTES = {15, 30, 60}


def _default_database_url() -> str:
    return "sqlite:///./runtime/profile/profile.sqlite3"


def _parse_origins(raw: str | None) -> list[str]:
    if not raw:
        return ["http://localhost:8095", "http://127.0.0.1:8095"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _parse_bool(raw: str | None, *, default: bool) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    database_url: str = field(default_factory=_default_database_url)
    safety_mode: str = "local_only"
    allow_demo_private_keys: bool = True
    admin_token: str = "local-profile-admin-token"
    app_version: str = "0.1.0"
    default_ttl_seconds: int = 900
    audit_timestamp_bucket_minutes: int = 60
    cors_origins: list[str] = field(default_factory=lambda: _parse_origins(None))

    def __post_init__(self) -> None:
        self.validate()

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            database_url=os.getenv("PROFILE_DATABASE_URL", _default_database_url()),
            safety_mode=os.getenv("PROFILE_SAFETY_MODE", "local_only"),
            allow_demo_private_keys=_parse_bool(os.getenv("PROFILE_ALLOW_DEMO_PRIVATE_KEYS"), default=True),
            admin_token=os.getenv("PROFILE_ADMIN_TOKEN", "local-profile-admin-token"),
            app_version=os.getenv("PROFILE_API_VERSION", "0.1.0"),
            default_ttl_seconds=int(os.getenv("PROFILE_DEFAULT_TTL_SECONDS", "900")),
            audit_timestamp_bucket_minutes=int(os.getenv("PROFILE_AUDIT_TIMESTAMP_BUCKET_MINUTES", "60")),
            cors_origins=_parse_origins(os.getenv("PROFILE_CORS_ORIGINS")),
        )

    def validate(self) -> None:
        if self.audit_timestamp_bucket_minutes not in SUPPORTED_AUDIT_TIMESTAMP_BUCKET_MINUTES:
            supported = ", ".join(str(value) for value in sorted(SUPPORTED_AUDIT_TIMESTAMP_BUCKET_MINUTES))
            raise ValueError(f"PROFILE_AUDIT_TIMESTAMP_BUCKET_MINUTES must be one of: {supported}")
        if self.safety_mode != "local_only" and self.allow_demo_private_keys:
            raise ValueError(
                "PROFILE_ALLOW_DEMO_PRIVATE_KEYS=true is only allowed when PROFILE_SAFETY_MODE=local_only"
            )

    @property
    def storage_backend(self) -> str:
        return "sqlite" if self.database_url.startswith("sqlite") else "sqlalchemy"

    def ensure_storage_parent(self) -> None:
        if not self.database_url.startswith("sqlite:///"):
            return
        path = self.database_url.replace("sqlite:///", "", 1)
        if path == ":memory:":
            return
        Path(path).parent.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    return Settings.from_env()
