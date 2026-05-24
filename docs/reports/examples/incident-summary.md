# Incident Summary: Route Policy Violation

Generated: 2026-05-24T20:28:49.598400+00:00
Severity: high
Affected component: android-route-guard

## What Happened

- `component`: `android-route-guard`
- `event_type`: `route_policy_violation`
- `redacted_session_ref`: `sess_2026_05_24_redacted`
- `route_scope`: `blocked_full_device_route`
- `safety_boundary`: `controlled_demo`

## Why It Matters

This event affects controlled release readiness because it touches a safety, validation, evidence, or operations boundary.

## Safety Boundary Impact

The event is handled inside the local controlled demo. It does not indicate public traffic forwarding or production security assurance.

## Recommended Action

Keep connection blocked, preserve redacted evidence, and review route guard changes.

## Evidence References

- Source event: `security/detection/sample-events/route_policy_violation.json`
- Detection report: `runtime/reports/siem-detection-report.md`
- Production readiness report: `runtime/reports/production-readiness-report.md`

## Known Limitations

This deterministic summary uses redacted event fields only. It is not an external LLM result and should be reviewed by an operator.
