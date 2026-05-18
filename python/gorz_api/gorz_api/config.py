from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _default_database_url() -> str:
    return "sqlite:///./runtime/gorz/gorz.sqlite3"


def _parse_origins(raw: str | None) -> list[str]:
    if not raw:
        return ["http://localhost:5174", "http://127.0.0.1:5174"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@dataclass(slots=True)
class Settings:
    database_url: str = field(default_factory=_default_database_url)
    safety_mode: str = "local-demo"
    app_version: str = "0.1.0"
    cors_origins: list[str] = field(default_factory=lambda: _parse_origins(None))

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            database_url=os.getenv("GORZ_DATABASE_URL", _default_database_url()),
            safety_mode=os.getenv("GORZ_SAFETY_MODE", "local-demo"),
            app_version=os.getenv("GORZ_API_VERSION", "0.1.0"),
            cors_origins=_parse_origins(os.getenv("GORZ_CORS_ORIGINS")),
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
