from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .audit import audit_page, export_audit_bundle, record_audit
from .config import Settings, get_settings
from .device_registry import device_response, register_device
from .diagnostics import simulate_diagnostic
from .issuer_keys import get_or_create_active_issuer_key, rotate_issuer_key
from .models import Device, SessionProfile, utc_now
from .openapi_tags import OPENAPI_TAGS
from .profile_issuer import ProfileIssueDenied, issue_session_profile, profile_metadata, validate_profile
from .revocation import revoke_profile
from .safety import get_safety_state, safety_response, set_pause
from .schemas import (
    AuditExportBundle,
    AuditPage,
    DeviceRegisterRequest,
    DeviceRegisterResponse,
    DeviceResponse,
    DiagnosticRequest,
    DiagnosticResponse,
    HealthResponse,
    IssuerRotateRequest,
    IssuerRotateResponse,
    ProfileValidationResponse,
    RevokeProfileRequest,
    RevokeProfileResponse,
    SafetyResponse,
    SessionProfileEnvelope,
    SessionProfileMetadata,
    SessionProfileRequest,
)
from .storage import get_session, init_db, session_factory


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    init_db(settings)
    with session_factory()() as session:
        get_or_create_active_issuer_key(session)
        session.commit()

    app = FastAPI(
        title="Gozar Profile API",
        version=settings.app_version,
        description=(
            "Local-only profile lifecycle API for signed encrypted profile envelopes. "
            "This service issues simulated profiles only and is not production secure."
        ),
        openapi_tags=OPENAPI_TAGS,
    )
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/profile/health", response_model=HealthResponse, tags=["health"])
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            version=settings.app_version,
            safety_mode=settings.safety_mode,
            storage_backend=settings.storage_backend,
            timestamp=utc_now(),
        )

    @app.post("/api/profile/devices/register", response_model=DeviceRegisterResponse, tags=["devices"])
    def register(payload: DeviceRegisterRequest, session: Session = Depends(get_session)) -> DeviceRegisterResponse:
        try:
            device, status = register_device(session, payload)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        session.commit()
        return DeviceRegisterResponse(
            device_id=device.device_id,
            device_public_key_hash=device.device_public_key_hash,
            registration_status=status,
            safety_notice="Local demo registration only. No production VPN profile is installed.",
        )

    @app.get("/api/profile/devices", response_model=list[DeviceResponse], tags=["devices"])
    def list_devices(session: Session = Depends(get_session)) -> list[dict[str, object]]:
        devices = session.scalars(select(Device).order_by(Device.created_at, Device.device_id)).all()
        return [device_response(device) for device in devices]

    @app.post("/api/profile/session-profiles", response_model=SessionProfileEnvelope, tags=["profiles"])
    def request_profile(
        payload: SessionProfileRequest,
        request: Request,
        session: Session = Depends(get_session),
    ) -> dict[str, object]:
        device = session.get(Device, payload.device_id)
        if device is None:
            raise HTTPException(status_code=404, detail="Device not found")
        try:
            envelope = issue_session_profile(
                session=session,
                device=device,
                request=payload,
                default_ttl_seconds=request.app.state.settings.default_ttl_seconds,
            )
        except ProfileIssueDenied as exc:
            session.commit()
            status_code = 423 if "safety_pause_enabled" in exc.decision.get("safety_notes", []) else 400
            raise HTTPException(status_code=status_code, detail=exc.decision) from exc
        session.commit()
        return envelope

    @app.get("/api/profile/session-profiles/{profile_id}", response_model=SessionProfileMetadata, tags=["profiles"])
    def get_profile(profile_id: str, session: Session = Depends(get_session)) -> dict[str, object]:
        profile = session.get(SessionProfile, profile_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile_metadata(profile)

    @app.post(
        "/api/profile/session-profiles/{profile_id}/validate",
        response_model=ProfileValidationResponse,
        tags=["profiles"],
    )
    def validate(profile_id: str, session: Session = Depends(get_session)) -> dict[str, object]:
        result = validate_profile(session, profile_id)
        session.commit()
        return result

    @app.post(
        "/api/profile/session-profiles/{profile_id}/revoke",
        response_model=RevokeProfileResponse,
        tags=["profiles"],
    )
    def revoke(
        profile_id: str,
        payload: RevokeProfileRequest,
        session: Session = Depends(get_session),
    ) -> RevokeProfileResponse:
        try:
            revoked = revoke_profile(session, profile_id, payload.reason)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Profile not found") from exc
        session.commit()
        return RevokeProfileResponse(
            profile_id=profile_id,
            status="revoked",
            revoked_at=revoked.revoked_at,
            reason=payload.reason,
        )

    @app.post("/api/profile/diagnostics/simulate", response_model=DiagnosticResponse, tags=["diagnostics"])
    def diagnostics(payload: DiagnosticRequest, session: Session = Depends(get_session)) -> dict[str, object]:
        result = simulate_diagnostic(session, payload.scenario)
        session.commit()
        return result

    @app.post("/api/profile/issuer/rotate-demo-key", response_model=IssuerRotateResponse, tags=["issuer"])
    def rotate_demo_key(payload: IssuerRotateRequest, session: Session = Depends(get_session)) -> IssuerRotateResponse:
        old_key, new_key = rotate_issuer_key(session, payload.reason)
        session.commit()
        return IssuerRotateResponse(
            old_key_id=old_key.key_id if old_key else None,
            new_key_id=new_key.key_id,
            active=new_key.active,
            safety_note=new_key.safety_note,
        )

    @app.get("/api/profile/audit", response_model=AuditPage, tags=["audit"])
    def audit(limit: int = 100, offset: int = 0, session: Session = Depends(get_session)) -> dict[str, object]:
        return audit_page(session, limit=min(max(limit, 1), 500), offset=max(offset, 0))

    @app.get("/api/profile/audit/export", response_model=AuditExportBundle, tags=["audit"])
    def audit_export(session: Session = Depends(get_session)) -> dict[str, object]:
        return export_audit_bundle(session)

    @app.get("/api/profile/safety", response_model=SafetyResponse, tags=["safety"])
    def safety(session: Session = Depends(get_session)) -> dict[str, object]:
        return safety_response(get_safety_state(session))

    @app.post("/api/profile/safety/pause", response_model=SafetyResponse, tags=["safety"])
    def pause(session: Session = Depends(get_session)) -> dict[str, object]:
        state = set_pause(session, True)
        record_audit(
            session,
            "safety.pause_enabled",
            summary="Safety pause enabled; new profile issuance is disabled.",
            metadata={"pause_enabled": True},
        )
        session.commit()
        return safety_response(state)

    @app.post("/api/profile/safety/resume", response_model=SafetyResponse, tags=["safety"])
    def resume(session: Session = Depends(get_session)) -> dict[str, object]:
        state = set_pause(session, False)
        record_audit(
            session,
            "safety.pause_disabled",
            summary="Safety pause disabled; local demo profile issuance may resume.",
            metadata={"pause_enabled": False},
        )
        session.commit()
        return safety_response(state)

    return app


app = create_app()
