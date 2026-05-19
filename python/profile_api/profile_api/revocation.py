from __future__ import annotations

from sqlalchemy.orm import Session

from .audit import record_audit
from .models import RevokedProfile, SessionProfile, utc_now


def revoke_profile(session: Session, profile_id: str, reason: str) -> RevokedProfile:
    profile = session.get(SessionProfile, profile_id)
    if profile is None:
        raise KeyError("profile not found")

    existing = session.get(RevokedProfile, profile_id)
    if existing is not None:
        return existing

    revoked = RevokedProfile(profile_id=profile_id, reason=reason, revoked_at=utc_now())
    profile.status = "revoked"
    session.add(revoked)
    record_audit(
        session,
        "profile.revoked",
        actor_id=profile.device_id_hash,
        summary="Local demo profile revoked.",
        metadata={"profile_id": profile_id, "reason": reason},
    )
    return revoked

