# Phase 4 Confidence Model

The Phase 4 confidence model is deterministic and prototype-scoped. It is not a production risk engine.

## Signals

| Signal | Meaning |
| --- | --- |
| Profile freshness | Profile TTL must still be active. |
| Issuer signature | Demo or backend signature verification must pass. |
| Revocation state | Revoked profiles are blocked. |
| Route policy | Only controlled local route scopes are accepted. |
| Endpoint scope | Only local or controlled lab labels are accepted. |
| Safety notes | Required safety notes must be present. |
| Diagnostics | Local diagnostics can request review. |
| VPN lifecycle | Android lifecycle remains local and packet-dropping. |
| Evidence redaction | Evidence generation improves review completeness. |
| Storage mode | Demo storage is a review penalty. |
| Offline demo mode | Offline mode is allowed with a small penalty. |
| Backend availability | Backend unavailability is a review penalty in offline demo. |
| Safety pause state | Active pause blocks connect. |

## Scoring

The score starts at 100. Blocking states force `BLOCKED`: invalid signature, revoked profile, expired profile, unsafe route, unsafe endpoint, and active safety pause. Missing safety notes subtracts 10. Backend unavailable in offline demo subtracts 5. Demo storage subtracts 5. Diagnostics review subtracts 5. Evidence not generated subtracts 3. Scores are clamped from 0 to 100.

## Status

| Status | Rule |
| --- | --- |
| HIGH | 85 to 100 with no blocking reasons. |
| REVIEW | 60 to 84 with no blocking reasons. |
| BLOCKED | Any blocking reason or score below 60. |

## Examples

- Fresh profile, accepted signature, no pause, accepted route: `HIGH`.
- Offline demo with demo storage and no generated evidence: `HIGH` or `REVIEW` depending on diagnostics.
- Expired profile: `BLOCKED`.
- Unsafe route or endpoint: `BLOCKED`.

## Limitations

The model is explainable and deterministic. It does not claim AI decisioning, production trust, guaranteed connectivity, or real-world security assurance.

## Future Direction

Future production expansion would need independent review, evidence fusion design, abuse governance, tenant-aware controls, and operational telemetry with privacy review.
