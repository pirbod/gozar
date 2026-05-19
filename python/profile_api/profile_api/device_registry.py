from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .audit import record_audit
from .crypto import public_key_fingerprint
from .models import Device, utc_now
from .schemas import DeviceRegisterRequest
from .storage import dumps_json, loads_json, new_id


def register_device(session: Session, payload: DeviceRegisterRequest) -> tuple[Device, str]:
    public_key_hash = public_key_fingerprint(payload.device_public_key)
    existing = session.scalar(select(Device).where(Device.device_public_key_hash == public_key_hash))
    if existing is not None:
        existing.display_name = payload.display_name
        existing.platform = payload.platform
        existing.app_version = payload.app_version
        existing.capabilities_json = dumps_json(payload.capabilities.model_dump())
        existing.updated_at = utc_now()
        record_audit(
            session,
            "device.registered",
            actor_id=existing.device_id,
            summary="Local demo device registration reused an existing public key hash.",
            metadata={"device_id": existing.device_id, "device_key_hash": public_key_hash},
        )
        return existing, "already_registered"

    device = Device(
        device_id=new_id("dev"),
        display_name=payload.display_name,
        platform=payload.platform,
        app_version=payload.app_version,
        device_public_key=payload.device_public_key,
        device_public_key_hash=public_key_hash,
        capabilities_json=dumps_json(payload.capabilities.model_dump()),
    )
    session.add(device)
    record_audit(
        session,
        "device.registered",
        actor_id=device.device_id,
        summary="Local demo device registered by public key hash.",
        metadata={"device_id": device.device_id, "device_key_hash": public_key_hash},
    )
    return device, "registered"


def device_response(device: Device) -> dict[str, object]:
    return {
        "device_id": device.device_id,
        "display_name": device.display_name,
        "platform": device.platform,
        "app_version": device.app_version,
        "device_public_key_hash": device.device_public_key_hash,
        "capabilities": loads_json(device.capabilities_json),
        "created_at": device.created_at,
    }
