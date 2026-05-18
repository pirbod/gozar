from __future__ import annotations

import json
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .audit import record_audit
from .config import Settings, get_settings
from .crypto_demo import encrypt_demo_envelope, generate_demo_keypair, hash_envelope
from .diagnostics import available_scenarios, delivery_evidence_for_message, simulate_scenario
from .incidents import build_incident_record, contains_forbidden_plaintext, redacted_preview
from .models import (
    AuditEvent,
    Conversation,
    ConversationParticipant,
    Device,
    Identity,
    Incident,
    Message,
    MessageEvidence,
    utc_now,
)
from .openapi_tags import OPENAPI_TAGS
from .safety import LIMITATIONS, get_safety_state, set_pause
from .schemas import (
    AuditPage,
    AuditResponse,
    ConversationCreate,
    ConversationDetail,
    ConversationSummary,
    DiagnosticResponse,
    HealthResponse,
    IdentityCreate,
    IdentityResponse,
    IncidentResponse,
    MessageCreate,
    MessageResponse,
    SafetyResponse,
    ScenarioInfo,
)
from .storage import dumps_json, get_session, init_db, loads_json, new_id


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    init_db(settings)

    app = FastAPI(
        title="Gorz Local Prototype API",
        version=settings.app_version,
        description=(
            "Local-first API for a safety-aware Gorz prototype. Diagnostics are simulated, "
            "message envelopes use demo cryptography, and the service is not for real sensitive communication."
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

    @app.get("/api/gorz/health", response_model=HealthResponse, tags=["health"])
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            version=settings.app_version,
            safety_mode=settings.safety_mode,
            storage_backend=settings.storage_backend,
            timestamp=utc_now(),
        )

    @app.post("/api/gorz/identities", response_model=IdentityResponse, tags=["identity"])
    def create_identity(payload: IdentityCreate, session: Session = Depends(get_session)) -> IdentityResponse:
        public_key, _private_key = generate_demo_keypair()
        identity = Identity(
            identity_id=new_id("ident"),
            display_name=payload.display_name,
            public_key_demo=public_key,
        )
        device = Device(
            device_id=new_id("dev"),
            identity_id=identity.identity_id,
            device_label=payload.device_label,
            public_key_demo=public_key,
        )
        session.add_all([identity, device])
        record_audit(
            session,
            "identity.created",
            actor_id=identity.identity_id,
            summary="Local demo identity created.",
            metadata={"device_id": device.device_id},
        )
        session.commit()
        return _identity_response(identity, device)

    @app.get("/api/gorz/identities", response_model=list[IdentityResponse], tags=["identity"])
    def list_identities(session: Session = Depends(get_session)) -> list[IdentityResponse]:
        identities = session.scalars(select(Identity).order_by(Identity.created_at)).all()
        responses: list[IdentityResponse] = []
        for identity in identities:
            device = session.scalar(select(Device).where(Device.identity_id == identity.identity_id))
            responses.append(_identity_response(identity, device))
        return responses

    @app.post("/api/gorz/conversations", response_model=ConversationSummary, tags=["conversations"])
    def create_conversation(
        payload: ConversationCreate, session: Session = Depends(get_session)
    ) -> ConversationSummary:
        participant_ids = list(dict.fromkeys(payload.participant_ids))
        if len(participant_ids) != len(payload.participant_ids):
            raise HTTPException(status_code=400, detail="participant_ids must be unique")
        found = session.scalars(select(Identity).where(Identity.identity_id.in_(participant_ids))).all()
        if len(found) != len(participant_ids):
            raise HTTPException(status_code=404, detail="One or more participants were not found")
        conversation = Conversation(conversation_id=new_id("conv"), title=payload.title)
        session.add(conversation)
        for participant_id in participant_ids:
            session.add(
                ConversationParticipant(
                    conversation_id=conversation.conversation_id,
                    identity_id=participant_id,
                )
            )
        record_audit(
            session,
            "conversation.created",
            summary="Local demo conversation created.",
            metadata={"conversation_id": conversation.conversation_id, "participants": len(participant_ids)},
        )
        session.commit()
        return _conversation_summary(session, conversation)

    @app.get("/api/gorz/conversations", response_model=list[ConversationSummary], tags=["conversations"])
    def list_conversations(session: Session = Depends(get_session)) -> list[ConversationSummary]:
        conversations = session.scalars(select(Conversation).order_by(Conversation.created_at)).all()
        return [_conversation_summary(session, conversation) for conversation in conversations]

    @app.get(
        "/api/gorz/conversations/{conversation_id}",
        response_model=ConversationDetail,
        tags=["conversations"],
    )
    def get_conversation(conversation_id: str, session: Session = Depends(get_session)) -> ConversationDetail:
        conversation = _require_conversation(session, conversation_id)
        summary = _conversation_summary(session, conversation)
        messages = session.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at, Message.message_id)
        ).all()
        return ConversationDetail(
            **summary.model_dump(),
            messages=[_message_response(session, message) for message in messages],
        )

    @app.post("/api/gorz/messages", response_model=MessageResponse, tags=["messages"])
    def create_message(payload: MessageCreate, session: Session = Depends(get_session)) -> MessageResponse:
        state = get_safety_state(session)
        if state.pause_enabled:
            raise HTTPException(status_code=423, detail="Emergency pause is active; demo sends are disabled")

        conversation = _require_conversation(session, payload.conversation_id)
        participant_ids = _participant_ids(session, conversation.conversation_id)
        if payload.sender_id not in participant_ids:
            raise HTTPException(status_code=400, detail="sender_id is not a conversation participant")
        sender = session.get(Identity, payload.sender_id)
        if sender is None:
            raise HTTPException(status_code=404, detail="sender_id was not found")
        recipient = _recipient_identity(session, participant_ids, payload.sender_id)

        ciphertext = encrypt_demo_envelope(payload.body, recipient.public_key_demo)
        envelope_hash = hash_envelope(ciphertext)
        evidence = delivery_evidence_for_message(payload.scenario, envelope_hash)
        diagnostic = evidence["diagnostic"]
        assert isinstance(diagnostic, dict)

        message = Message(
            message_id=new_id("msg"),
            conversation_id=conversation.conversation_id,
            sender_id=payload.sender_id,
            scenario=payload.scenario,
            redacted_preview=redacted_preview(payload.body),
            ciphertext_demo=ciphertext,
            envelope_hash=envelope_hash,
            delivery_status=str(diagnostic["classification"]),
            confidence=float(diagnostic["confidence"]),
            redaction_status="plaintext_discarded_after_demo_envelope_creation",
        )
        session.add(message)
        session.flush()
        session.add(
            MessageEvidence(
                evidence_id=new_id("evd"),
                message_id=message.message_id,
                evidence_json=dumps_json(evidence),
            )
        )
        record_audit(
            session,
            "message.envelope_created",
            actor_id=payload.sender_id,
            summary="Demo encrypted envelope created and plaintext discarded.",
            metadata={"message_id": message.message_id, "conversation_id": conversation.conversation_id},
        )
        record_audit(
            session,
            "message.delivery_scored",
            actor_id=payload.sender_id,
            summary="Delivery confidence scored by Python engine.",
            metadata={
                "message_id": message.message_id,
                "scenario": payload.scenario,
                "classification": message.delivery_status,
                "confidence": message.confidence,
            },
        )
        session.commit()
        response = _message_response(session, message)
        if contains_forbidden_plaintext(response.model_dump(), payload.body):
            raise HTTPException(status_code=500, detail="Plaintext redaction verification failed")
        return response

    @app.get("/api/gorz/messages/{message_id}", response_model=MessageResponse, tags=["messages"])
    def get_message(message_id: str, session: Session = Depends(get_session)) -> MessageResponse:
        message = session.get(Message, message_id)
        if message is None:
            raise HTTPException(status_code=404, detail="Message not found")
        return _message_response(session, message)

    @app.post(
        "/api/gorz/diagnostics/simulate",
        response_model=DiagnosticResponse,
        tags=["diagnostics"],
    )
    def simulate_diagnostics(payload: dict[str, str], session: Session = Depends(get_session)) -> dict[str, Any]:
        scenario = payload.get("scenario", "")
        try:
            result = simulate_scenario(scenario)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        record_audit(
            session,
            "diagnostic.simulated",
            summary="Local diagnostic scenario simulated.",
            metadata={"scenario": scenario},
        )
        session.commit()
        return result

    @app.get("/api/gorz/diagnostics/scenarios", response_model=list[ScenarioInfo], tags=["diagnostics"])
    def get_scenarios() -> list[dict[str, str]]:
        return available_scenarios()

    @app.post(
        "/api/gorz/incidents/from-message/{message_id}",
        response_model=IncidentResponse,
        tags=["incidents"],
    )
    def incident_from_message(message_id: str, session: Session = Depends(get_session)) -> IncidentResponse:
        message = session.get(Message, message_id)
        if message is None:
            raise HTTPException(status_code=404, detail="Message not found")
        evidence = _message_evidence(session, message.message_id)
        incident = Incident(
            incident_id=new_id("inc"),
            message_id=message.message_id,
            conversation_id=message.conversation_id,
            record_json="{}",
        )
        session.add(incident)
        session.flush()
        record = build_incident_record(
            incident_id=incident.incident_id,
            created_at=incident.created_at,
            message_id=message.message_id,
            conversation_id=message.conversation_id,
            message_created_at=message.created_at,
            classification=message.delivery_status,
            confidence=message.confidence,
            envelope_hash=message.envelope_hash,
            scenario=message.scenario,
            evidence_json=evidence.evidence_json,
        )
        incident.record_json = dumps_json(record)
        record_audit(
            session,
            "incident.generated",
            summary="Redacted incident package generated from message evidence.",
            metadata={"incident_id": incident.incident_id, "message_id": message.message_id},
        )
        session.commit()
        return IncidentResponse(
            incident_id=incident.incident_id,
            created_at=incident.created_at,
            record=record,
        )

    @app.get("/api/gorz/incidents", response_model=list[IncidentResponse], tags=["incidents"])
    def list_incidents(session: Session = Depends(get_session)) -> list[IncidentResponse]:
        incidents = session.scalars(select(Incident).order_by(Incident.created_at.desc())).all()
        return [_incident_response(incident) for incident in incidents]

    @app.get("/api/gorz/incidents/{incident_id}", response_model=IncidentResponse, tags=["incidents"])
    def get_incident(incident_id: str, session: Session = Depends(get_session)) -> IncidentResponse:
        incident = session.get(Incident, incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        return _incident_response(incident)

    @app.get("/api/gorz/incidents/{incident_id}/download", tags=["incidents"])
    def download_incident(incident_id: str, session: Session = Depends(get_session)) -> Response:
        incident = session.get(Incident, incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        return Response(
            content=json.dumps(loads_json(incident.record_json), indent=2, sort_keys=True),
            media_type="application/json",
            headers={"content-disposition": f'attachment; filename="gorz-incident-{incident_id}.json"'},
        )

    @app.get("/api/gorz/audit", response_model=AuditPage, tags=["audit"])
    def list_audit(
        limit: int = 50,
        offset: int = 0,
        session: Session = Depends(get_session),
    ) -> AuditPage:
        limit = min(max(limit, 1), 200)
        offset = max(offset, 0)
        total = session.scalar(select(func.count()).select_from(AuditEvent)) or 0
        events = session.scalars(
            select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit).offset(offset)
        ).all()
        return AuditPage(
            items=[_audit_response(event) for event in events],
            limit=limit,
            offset=offset,
            total=total,
        )

    @app.get("/api/gorz/safety", response_model=SafetyResponse, tags=["safety"])
    def get_safety(session: Session = Depends(get_session)) -> SafetyResponse:
        state = get_safety_state(session)
        return SafetyResponse(
            safety_mode=settings.safety_mode,
            pause_enabled=state.pause_enabled,
            limitations=LIMITATIONS,
            updated_at=state.updated_at,
        )

    @app.post("/api/gorz/safety/pause", response_model=SafetyResponse, tags=["safety"])
    def pause_sends(session: Session = Depends(get_session)) -> SafetyResponse:
        state = set_pause(session, True)
        record_audit(
            session,
            "safety.pause_enabled",
            summary="Emergency pause enabled for local demo sends.",
            metadata={},
        )
        session.commit()
        return SafetyResponse(
            safety_mode=settings.safety_mode,
            pause_enabled=state.pause_enabled,
            limitations=LIMITATIONS,
            updated_at=state.updated_at,
        )

    @app.post("/api/gorz/safety/resume", response_model=SafetyResponse, tags=["safety"])
    def resume_sends(session: Session = Depends(get_session)) -> SafetyResponse:
        state = set_pause(session, False)
        record_audit(
            session,
            "safety.pause_disabled",
            summary="Emergency pause disabled for local demo sends.",
            metadata={},
        )
        session.commit()
        return SafetyResponse(
            safety_mode=settings.safety_mode,
            pause_enabled=state.pause_enabled,
            limitations=LIMITATIONS,
            updated_at=state.updated_at,
        )

    return app


def _identity_response(identity: Identity, device: Device | None) -> IdentityResponse:
    return IdentityResponse(
        identity_id=identity.identity_id,
        device_id=device.device_id if device else None,
        display_name=identity.display_name,
        device_label=device.device_label if device else None,
        public_key_demo=identity.public_key_demo,
        safety_notice="Local demo identity. Demo key material is not production cryptography.",
        created_at=identity.created_at,
    )


def _participant_ids(session: Session, conversation_id: str) -> list[str]:
    return list(
        session.scalars(
            select(ConversationParticipant.identity_id)
            .where(ConversationParticipant.conversation_id == conversation_id)
            .order_by(ConversationParticipant.identity_id)
        ).all()
    )


def _conversation_summary(session: Session, conversation: Conversation) -> ConversationSummary:
    return ConversationSummary(
        conversation_id=conversation.conversation_id,
        title=conversation.title,
        participant_ids=_participant_ids(session, conversation.conversation_id),
        created_at=conversation.created_at,
    )


def _require_conversation(session: Session, conversation_id: str) -> Conversation:
    conversation = session.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


def _recipient_identity(session: Session, participant_ids: list[str], sender_id: str) -> Identity:
    recipient_id = next((identity_id for identity_id in participant_ids if identity_id != sender_id), sender_id)
    recipient = session.get(Identity, recipient_id)
    if recipient is None:
        raise HTTPException(status_code=404, detail="Recipient identity not found")
    return recipient


def _message_evidence(session: Session, message_id: str) -> MessageEvidence:
    evidence = session.scalar(select(MessageEvidence).where(MessageEvidence.message_id == message_id))
    if evidence is None:
        raise HTTPException(status_code=404, detail="Message evidence not found")
    return evidence


def _message_response(session: Session, message: Message) -> MessageResponse:
    evidence = _message_evidence(session, message.message_id)
    return MessageResponse(
        message_id=message.message_id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        scenario=message.scenario,  # type: ignore[arg-type]
        redacted_preview=message.redacted_preview,
        envelope_hash=message.envelope_hash,
        delivery_status=message.delivery_status,  # type: ignore[arg-type]
        confidence=message.confidence,
        evidence=loads_json(evidence.evidence_json),
        redaction_status=message.redaction_status,
        created_at=message.created_at,
    )


def _incident_response(incident: Incident) -> IncidentResponse:
    return IncidentResponse(
        incident_id=incident.incident_id,
        created_at=incident.created_at,
        record=loads_json(incident.record_json),
    )


def _audit_response(event: AuditEvent) -> AuditResponse:
    return AuditResponse(
        event_id=event.event_id,
        event_type=event.event_type,
        actor_id=event.actor_id,
        summary=event.summary,
        metadata=loads_json(event.metadata_json),
        created_at=event.created_at,
    )


app = create_app()
