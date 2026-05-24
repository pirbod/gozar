# Backend Alpha Hardening

## Current Local-Only Status

Gorz API and Profile API are local-first demo backends. They support confidence scoring, profile lifecycle validation, safety pause, diagnostics simulation, redacted audit, and evidence flows for controlled evaluation.

## Authentication Limitations

Current auth is local demo oriented. It is not a tenant-aware production auth model and must not be used as a real access-control system.

## Admin Token Limitation

Static demo admin tokens protect sensitive local endpoints. Alpha requires managed secrets, rotation, least privilege, and audit review.

## SQLite Limitation

SQLite is acceptable for local demo state. Alpha and production require a managed database plan, migrations, backups, retention, and access controls.

## CORS Limitation

Current CORS behavior is suitable for local demos only. Alpha should lock origins to explicit demo hosts and production should use environment-specific policy.

## Audit Logging Model

Audit logs capture profile lifecycle, safety actions, diagnostics, evidence, and local operator events. Logs must remain redacted and should not contain plaintext payloads.

## Redaction Model

Redaction removes or hashes sensitive IDs, plaintext bodies, local endpoints, encrypted payloads, and signatures where appropriate.

## Safety Pause Model

Safety pause blocks new message sends in Gorz API and new profile issuance in Profile API. It must remain enforceable in every environment.

## Production Tenant Gap

No production tenant model exists. Add tenant boundaries, scoped roles, authentication, authorization, and audit identity before alpha pilots.

## Rate Limiting Gap

No production rate limiter is implemented. See `docs/backend/rate-limiting-design.md`.

## Secret Management Gap

Secrets are local demo values. Alpha requires environment-specific secret storage, rotation, and deployment controls.
