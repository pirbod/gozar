# Safety Boundaries

Phase 1 is local-only and Docker-only. It demonstrates signed encrypted profile lifecycle mechanics without producing a real connectivity product.

## Boundaries

- No OS VPN installation.
- No public gateways.
- No public network probing.
- No endpoint scraping.
- No automatic platform adapter.
- No production secure claim.
- No use for real sensitive communication.
- Not a circumvention tool.

## Safety Pause

`POST /api/profile/safety/pause` blocks new profile issuance. Validation and audit export remain available so developers can inspect lifecycle state. `POST /api/profile/safety/resume` restores local demo issuance.

## Diagnostics

Diagnostics are simulated. They do not run public network checks, collect location, or discover endpoints.

