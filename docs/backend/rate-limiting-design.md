# Rate Limiting Design

## Why Rate Limiting Is Needed

Rate limiting protects profile issuance, admin endpoints, diagnostics, and evidence export from accidental or abusive load during pilots.

## Proposed Local/Dev Behavior

Local development should keep rate limiting disabled or permissive, with logs showing where rate limits would apply.

## Proposed Alpha Behavior

Alpha should apply conservative per-device and per-admin limits for profile issuance, safety actions, diagnostics simulation, and audit export.

## Proposed Production Behavior

Production would require tenant-aware quotas, burst controls, abuse response workflows, observability, and operator override controls.

## Risks And Controls

| Risk | Control |
| --- | --- |
| Legitimate demo blocked | Provide local override and clear error message. |
| Abuse not throttled | Add per-device and per-token limits. |
| Safety pause blocked by limiter | Exempt safety pause from rate limits. |
| Logs expose identifiers | Redact rate-limit audit metadata. |
