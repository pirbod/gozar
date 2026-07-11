from __future__ import annotations

import secrets

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy import text as sql_text
from sqlalchemy.orm import Session

from .audit import audit_page, export_audit_bundle, record_audit
from .config import Settings, get_settings
from .device_registry import device_response, register_device
from .diagnostics import simulate_diagnostic
from .issuer_keys import get_or_create_active_issuer_key, rotate_issuer_key
from .models import Device, SessionProfile, utc_now
from .openapi_tags import OPENAPI_TAGS
from .private_access import (
    DeviceAuthenticationError,
    PrivateAccessDenied,
    authenticate_device,
    device_summary,
    enroll_device,
    issue_access_profile,
    validate_access_profile,
    wireguard_peers,
)
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
    MobileBootstrapResponse,
    PrivateAccessDeviceResponse,
    PrivateAccessEnrollmentRequest,
    PrivateAccessEnrollmentResponse,
    PrivateAccessProfileEnvelope,
    PrivateAccessProfileRequest,
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
    if settings.enable_demo_api:
        with session_factory()() as session:
            get_or_create_active_issuer_key(session, allow_demo_private_keys=settings.allow_demo_private_keys)
            session.commit()

    app = FastAPI(
        title="Gozar Profile API",
        version=settings.app_version,
        description=(
            "Device enrollment and short-lived WireGuard profiles for approved internal services. "
            "Legacy demo endpoints are available only in the development environment."
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

    @app.middleware("http")
    async def disable_legacy_demo_api(request: Request, call_next):
        if (
            not settings.enable_demo_api
            and request.url.path.startswith("/api/profile/")
            and request.url.path != "/api/profile/health"
        ):
            raise HTTPException(status_code=404, detail="Legacy demo API is disabled")
        return await call_next(request)

    def require_admin_token(request: Request) -> None:
        token = request.headers.get("x-profile-admin-token", "")
        if not secrets.compare_digest(token, settings.admin_token):
            raise HTTPException(status_code=401, detail="Operator authentication failed")

    def require_enrollment_token(request: Request) -> None:
        token = request.headers.get("x-gozar-enrollment-token", "")
        if not secrets.compare_digest(token, settings.enrollment_token):
            raise HTTPException(status_code=401, detail="Enrollment authentication failed")

    def require_device(
        request: Request,
        session: Session = Depends(get_session),
    ) -> Device:
        authorization = request.headers.get("authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(status_code=401, detail="Device bearer token is required")
        try:
            return authenticate_device(session, token, settings)
        except DeviceAuthenticationError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @app.get("/api/profile/health", response_model=HealthResponse, tags=["health"])
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            version=settings.app_version,
            safety_mode=settings.safety_mode,
            storage_backend=settings.storage_backend,
            timestamp=utc_now(),
        )

    @app.get("/livez", tags=["health"])
    def livez() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", tags=["health"])
    def readyz(session: Session = Depends(get_session)) -> dict[str, str]:
        session.execute(sql_text("SELECT 1"))
        return {"status": "ready", "storage": settings.storage_backend}

    @app.post(
        "/api/v1/enrollment",
        response_model=PrivateAccessEnrollmentResponse,
        tags=["private-access"],
        dependencies=[Depends(require_enrollment_token)],
    )
    def enroll(
        payload: PrivateAccessEnrollmentRequest,
        session: Session = Depends(get_session),
    ) -> dict[str, object]:
        try:
            device, raw_token = enroll_device(session, payload, settings)
        except (ValueError, PrivateAccessDenied) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        session.commit()
        return {
            "device_id": device.device_id,
            "device_token": raw_token,
            "assigned_address": str(device.assigned_address),
            "status": "active",
            "token_type": "Bearer",
        }

    @app.get("/api/v1/me", response_model=PrivateAccessDeviceResponse, tags=["private-access"])
    def me(
        device: Device = Depends(require_device),
        session: Session = Depends(get_session),
    ) -> dict[str, object]:
        response = device_summary(device, settings)
        session.commit()
        return response

    @app.post(
        "/api/v1/access-profiles",
        response_model=PrivateAccessProfileEnvelope,
        tags=["private-access"],
    )
    def create_access_profile(
        payload: PrivateAccessProfileRequest,
        device: Device = Depends(require_device),
        session: Session = Depends(get_session),
    ) -> dict[str, object]:
        try:
            envelope = issue_access_profile(session, device, payload, settings)
        except PrivateAccessDenied as exc:
            raise HTTPException(status_code=423, detail=str(exc)) from exc
        session.commit()
        return envelope

    @app.post(
        "/api/v1/access-profiles/{profile_id}/validate",
        response_model=ProfileValidationResponse,
        tags=["private-access"],
    )
    def validate_private_access_profile(
        profile_id: str,
        device: Device = Depends(require_device),
        session: Session = Depends(get_session),
    ) -> dict[str, object]:
        result = validate_access_profile(session, profile_id, device)
        session.commit()
        if result["status"] == "unknown":
            raise HTTPException(status_code=404, detail="Profile not found")
        return result

    @app.get("/api/v1/admin/wireguard/peers", tags=["private-access"])
    def list_wireguard_peers(
        _: None = Depends(require_admin_token),
        session: Session = Depends(get_session),
    ) -> list[dict[str, str]]:
        return wireguard_peers(session)

    @app.post("/api/v1/admin/access/pause", tags=["private-access"])
    def pause_private_access(
        _: None = Depends(require_admin_token),
        session: Session = Depends(get_session),
    ) -> dict[str, object]:
        state = set_pause(session, True)
        record_audit(
            session,
            "private_access.pause_enabled",
            summary="Private-access profile issuance paused by an operator.",
            metadata={"pause_enabled": True},
        )
        session.commit()
        return safety_response(state)

    @app.post("/api/v1/admin/access/resume", tags=["private-access"])
    def resume_private_access(
        _: None = Depends(require_admin_token),
        session: Session = Depends(get_session),
    ) -> dict[str, object]:
        state = set_pause(session, False)
        record_audit(
            session,
            "private_access.pause_disabled",
            summary="Private-access profile issuance resumed by an operator.",
            metadata={"pause_enabled": False},
        )
        session.commit()
        return safety_response(state)

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

    @app.get("/api/profile/mobile/bootstrap", response_model=MobileBootstrapResponse, tags=["profiles"])
    def mobile_bootstrap(session: Session = Depends(get_session)) -> MobileBootstrapResponse:
        issuer_key = get_or_create_active_issuer_key(
            session,
            allow_demo_private_keys=settings.allow_demo_private_keys,
        )
        session.commit()
        return MobileBootstrapResponse(
            service="profile-api",
            mode="local-demo",
            issuer_public_key=issuer_key.public_key,
            default_ttl_seconds=settings.default_ttl_seconds,
            supported_profile_types=["wireguard_like_demo", "quic_like_demo"],
            android_emulator_api_url_hint="http://10.0.2.2:8095",
            safety_notes=[
                "local_demo_only",
                "signed_encrypted_profile",
                "short_lived_demo_config",
                "no_public_gateway",
                "no_external_probing",
                "android_local_demo_envelope_mode",
            ],
        )

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
        _: None = Depends(require_admin_token),
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
    def rotate_demo_key(
        payload: IssuerRotateRequest,
        _: None = Depends(require_admin_token),
        session: Session = Depends(get_session),
    ) -> IssuerRotateResponse:
        old_key, new_key = rotate_issuer_key(
            session,
            payload.reason,
            allow_demo_private_keys=settings.allow_demo_private_keys,
        )
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
        return export_audit_bundle(
            session,
            timestamp_bucket_minutes=settings.audit_timestamp_bucket_minutes,
        )

    @app.get("/api/profile/safety", response_model=SafetyResponse, tags=["safety"])
    def safety(session: Session = Depends(get_session)) -> dict[str, object]:
        return safety_response(get_safety_state(session))

    @app.post("/api/profile/safety/pause", response_model=SafetyResponse, tags=["safety"])
    def pause(
        _: None = Depends(require_admin_token),
        session: Session = Depends(get_session),
    ) -> dict[str, object]:
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
    def resume(
        _: None = Depends(require_admin_token),
        session: Session = Depends(get_session),
    ) -> dict[str, object]:
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
