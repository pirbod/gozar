# Gorz Production Prototype Plan

## Objective

Gorz applies the Gozar evidence model to a local messaging prototype. The goal is to show
confidence-aware delivery, safety-aware diagnostics, redacted incident evidence, auditability,
and a Python-first backend without claiming production security.

## Architecture

- Python FastAPI backend in `python/gorz_api`.
- SQLite local persistence for demo identities, conversations, encrypted-envelope records,
  delivery evidence, incidents, audit events, and safety state.
- React web UI in `ts/apps/gorz-web`.
- Docker Compose demo in `docker-compose.gorz.yml`.
- Local validation scripts in `scripts/gorz`.

## Backend Modules

- `main.py`: API routes and response assembly.
- `models.py`: SQLAlchemy tables.
- `storage.py`: SQLite setup and session handling.
- `crypto_demo.py`: demo-only envelope generation and hashing.
- `confidence.py`: bottleneck-aware confidence engine.
- `diagnostics.py`: local simulated scenarios.
- `incidents.py`: redacted incident package generation.
- `audit.py`: audit event writer.
- `safety.py`: emergency pause and limitations.

## Frontend Pages

- Messenger: identities, conversations, scenario selection, message send, timeline, confidence,
  and evidence.
- Diagnostics: scenario simulation and layer scores.
- Evidence: incident list, redaction summary, and JSON download.
- Safety: boundaries, emergency pause/resume, and audit trail.

## Safety Boundaries

Gorz is a lawful local demo. It does not scan public networks, discover relays, collect real IP
addresses, collect exact locations, upload diagnostics, or provide production secure messaging.
All diagnostics are simulated and local-only.

## What Is Simulated

- Message delivery paths.
- Peer receipts.
- Relay class behavior.
- Domestic-only, blocked, delayed, degraded, and peer-offline states.
- Diagnostic layer scores.

## What Is Not Implemented

- Production end-to-end encryption.
- Real account provisioning.
- Real external delivery.
- Public relay operation.
- Bridge or relay discovery.
- Automatic evidence upload.

## Future Production Path

Any future production path would require audited cryptography, a formal threat model, privacy
review, abuse review, external security audit, consent-based telemetry design, rigorous key
management, and a separate deployment architecture. This prototype intentionally stops before
those claims.

