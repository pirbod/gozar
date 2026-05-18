# Gorz API Contract

Base URL: `http://localhost:8090`

All endpoints return JSON unless noted. Errors use FastAPI's standard shape:

```json
{ "detail": "Human-readable error" }
```

## Health

`GET /api/gorz/health`

Returns service status, version, safety mode, storage backend, and timestamp.

## Identities

`POST /api/gorz/identities`

```json
{ "display_name": "Ari Local", "device_label": "Laptop" }
```

Returns a local demo identity, device id, demo public key, and safety notice.

`GET /api/gorz/identities`

Lists local demo identities.

## Conversations

`POST /api/gorz/conversations`

```json
{ "title": "Local demo conversation", "participant_ids": ["ident_a", "ident_b"] }
```

`GET /api/gorz/conversations`

Lists conversation summaries.

`GET /api/gorz/conversations/{conversation_id}`

Returns metadata and redacted message records.

## Messages

`POST /api/gorz/messages`

```json
{
  "conversation_id": "conv_123",
  "sender_id": "ident_123",
  "body": "demo message",
  "scenario": "direct_ok"
}
```

Scenarios: `direct_ok`, `relay_ok`, `delayed`, `degraded`, `domestic_only`, `blocked`,
`peer_offline`.

The backend creates a demo envelope, discards plaintext, stores a redacted preview, hashes the
envelope, computes confidence, stores delivery evidence, and writes audit events.

`GET /api/gorz/messages/{message_id}`

Returns metadata, envelope hash, delivery status, confidence, evidence, and redaction status.

## Diagnostics

`POST /api/gorz/diagnostics/simulate`

```json
{ "scenario": "degraded" }
```

Returns layer scores, risk penalty, confidence, classification, and explanation. This endpoint
does not call external targets.

`GET /api/gorz/diagnostics/scenarios`

Lists available local simulations.

## Incidents

`POST /api/gorz/incidents/from-message/{message_id}`

Generates a redacted incident package from stored message evidence.

`GET /api/gorz/incidents`

Lists generated incidents.

`GET /api/gorz/incidents/{incident_id}`

Returns the redacted incident record.

`GET /api/gorz/incidents/{incident_id}/download`

Downloads the redacted record as JSON.

## Audit

`GET /api/gorz/audit?limit=50&offset=0`

Returns audit events for identities, conversations, messages, diagnostics, incidents, and safety
pause/resume.

## Safety

`GET /api/gorz/safety`

Returns safety status and limitations.

`POST /api/gorz/safety/pause`

Enables emergency pause. New message sends return HTTP 423.

`POST /api/gorz/safety/resume`

Resumes local demo sends.

