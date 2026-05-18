from __future__ import annotations

from pathlib import Path

from sqlalchemy import select

from gorz_api.config import Settings
from gorz_api.crypto_demo import encrypt_demo_envelope, generate_demo_keypair, hash_envelope
from gorz_api.models import Identity
from gorz_api.storage import init_db, session_factory


def test_sqlite_persistence_works(tmp_path: Path) -> None:
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'persist.sqlite3'}")
    init_db(settings)
    public_key, _ = generate_demo_keypair()

    with session_factory()() as session:
        session.add(Identity(identity_id="ident_test", display_name="Persisted", public_key_demo=public_key))
        session.commit()

    init_db(settings)
    with session_factory()() as session:
        identity = session.scalar(select(Identity).where(Identity.identity_id == "ident_test"))
        assert identity is not None
        assert identity.display_name == "Persisted"


def test_demo_envelope_hash_is_stable_for_ciphertext() -> None:
    public_key, _ = generate_demo_keypair()
    ciphertext = encrypt_demo_envelope("hello", public_key)
    assert hash_envelope(ciphertext) == hash_envelope(ciphertext)
    assert hash_envelope(ciphertext).startswith("sha256:")

