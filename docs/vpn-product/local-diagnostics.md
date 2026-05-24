# Local Diagnostics

Phase 4 diagnostics are local-only and evidence-ready.

## Checks

- Profile API URL format
- Profile API health for local endpoints only
- Offline demo status
- Backend availability
- VPN lifecycle status
- Route policy validation
- Confidence status
- Evidence redaction state
- Safety pause state
- Storage mode
- Packet counter
- Mock path quality

## What Diagnostics Do Not Do

Diagnostics do not perform public DNS queries, public HTTP checks, network scanning, automatic upload, or packet contents capture.

## Local Boundaries

Allowed Profile API hosts are `localhost`, `127.0.0.1`, and `10.0.2.2`. Any other host is blocked before a health request is attempted.

## Expected Output

Diagnostics return `PASS`, `REVIEW`, or `BLOCKED`, a check list, summary, generation time, redaction state, and `localOnly: true`.

## Limitations

Diagnostics are useful for demo and review readiness. They are not a production observability system.
