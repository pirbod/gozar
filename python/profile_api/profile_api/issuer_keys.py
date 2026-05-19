from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .audit import record_audit
from .crypto import generate_issuer_signing_keypair
from .models import IssuerKey, utc_now
from .storage import new_id

ISSUER_SAFETY_NOTE = "Local demo key rotation only. Production requires KMS/HSM-backed signing."


def get_or_create_active_issuer_key(session: Session) -> IssuerKey:
    key = session.scalar(
        select(IssuerKey).where(IssuerKey.active.is_(True)).order_by(IssuerKey.created_at.desc(), IssuerKey.key_id)
    )
    if key is not None:
        return key
    public_key, private_key = generate_issuer_signing_keypair()
    key = IssuerKey(
        key_id=new_id("issuer"),
        public_key=public_key,
        private_key_demo=private_key,
        active=True,
        created_by="local-demo",
        safety_note=ISSUER_SAFETY_NOTE,
    )
    session.add(key)
    session.flush()
    return key


def rotate_issuer_key(session: Session, reason: str) -> tuple[IssuerKey | None, IssuerKey]:
    old_key = get_or_create_active_issuer_key(session)
    old_key.active = False
    old_key.expires_at = utc_now()
    old_key.rotation_reason = reason
    public_key, private_key = generate_issuer_signing_keypair()
    new_key = IssuerKey(
        key_id=new_id("issuer"),
        public_key=public_key,
        private_key_demo=private_key,
        active=True,
        rotation_reason=reason,
        created_by="local-demo",
        safety_note=ISSUER_SAFETY_NOTE,
    )
    session.add(new_key)
    record_audit(
        session,
        "issuer.demo_key_rotated",
        summary="Local demo issuer signing key rotated.",
        metadata={"old_key_id": old_key.key_id, "new_key_id": new_key.key_id, "reason": reason},
    )
    return old_key, new_key


def get_issuer_key(session: Session, key_id: str) -> IssuerKey | None:
    return session.get(IssuerKey, key_id)


def deactivate_issuer_key(session: Session, key_id: str, reason: str) -> IssuerKey:
    key = session.get(IssuerKey, key_id)
    if key is None:
        raise KeyError("issuer key not found")
    key.active = False
    key.expires_at = utc_now()
    key.rotation_reason = reason
    record_audit(
        session,
        "issuer.demo_key_deactivated",
        summary="Local demo issuer signing key deactivated.",
        metadata={"issuer_key_id": key.key_id, "reason": reason},
    )
    return key
