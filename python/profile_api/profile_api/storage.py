from __future__ import annotations

import json
from collections.abc import Generator
from uuid import uuid4

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import Settings, get_settings
from .models import Base, SafetyState

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:18]}"


def dumps_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def loads_json(raw: str) -> dict[str, object]:
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        return {}
    return parsed


def configure_database(settings: Settings | None = None) -> None:
    global _engine, _session_factory
    settings = settings or get_settings()
    settings.ensure_storage_parent()
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    _engine = create_engine(settings.database_url, connect_args=connect_args, future=True, pool_pre_ping=True)
    _session_factory = sessionmaker(bind=_engine, expire_on_commit=False, autoflush=False)


def engine() -> Engine:
    if _engine is None:
        configure_database()
    assert _engine is not None
    return _engine


def session_factory() -> sessionmaker[Session]:
    if _session_factory is None:
        configure_database()
    assert _session_factory is not None
    return _session_factory


def init_db(settings: Settings | None = None) -> None:
    if settings is not None:
        configure_database(settings)
    settings = settings or get_settings()
    if settings.environment in {"development", "test"}:
        Base.metadata.create_all(bind=engine())
    else:
        required_tables = {"devices", "session_profiles", "safety_state", "audit_events"}
        existing_tables = set(inspect(engine()).get_table_names())
        missing = sorted(required_tables - existing_tables)
        if missing:
            raise RuntimeError(
                "database migrations are required before startup; missing tables: " + ", ".join(missing)
            )
    with session_factory()() as session:
        state = session.scalar(select(SafetyState).where(SafetyState.state_id == "singleton"))
        if state is None:
            session.add(SafetyState(state_id="singleton", pause_enabled=False))
            session.commit()


def get_session() -> Generator[Session]:
    with session_factory()() as session:
        yield session
