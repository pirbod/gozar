from __future__ import annotations

import json
from collections.abc import Generator
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import Settings, get_settings
from .models import Base, IssuerKey, SafetyState

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
    _engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
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
    Base.metadata.create_all(bind=engine())
    with session_factory()() as session:
        state = session.scalar(select(SafetyState).where(SafetyState.state_id == "singleton"))
        if state is None:
            session.add(SafetyState(state_id="singleton", pause_enabled=False))
            session.commit()


def get_session() -> Generator[Session]:
    with session_factory()() as session:
        yield session


def store_issuer_public_key(session: Session, issuer_public_key: str) -> IssuerKey:
    key = session.scalar(select(IssuerKey).where(IssuerKey.issuer_public_key == issuer_public_key))
    if key is not None:
        return key
    session.query(IssuerKey).update({"active": False})
    key = IssuerKey(key_id=new_id("issuer"), issuer_public_key=issuer_public_key, active=True)
    session.add(key)
    session.commit()
    return key

