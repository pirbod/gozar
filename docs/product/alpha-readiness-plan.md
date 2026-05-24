# Alpha Readiness Plan

## Alpha Scope

The safe alpha demonstrates local-first messaging, adaptive demo profiles, Android mobile UX, local VPN lifecycle validation, redacted evidence, audit trails, and safety pause controls.

## Alpha Non-Goals

- No production VPN.
- No public routing product.
- No real secure messenger claim.
- No public network probing.
- No field deployment.
- No production cryptographic claims.

## Target Users

- Internal reviewers.
- Academic collaborators.
- Security engineers reviewing safety controls.
- Product stakeholders evaluating demo workflows.

## Required Controls

- Production readiness report.
- Android permission and route safety checks.
- Backend safety scanner.
- Redaction tests.
- Safety pause tests.
- Release blocker checklist.
- Manual Android Studio emulator validation.
- Emulator smoke test required for alpha readiness.

## Testing Strategy

PR gates should run Android build, Android unit tests when the toolchain is available, backend tests, safety checks, and production readiness checks. Emulator smoke should run nightly or manually if it is too unstable for PR gating. Manual Android Studio validation is required before demo release.

## Operational Model

Demos run locally with explicit operator control. Evidence exports are user-initiated. Operators can pause sessions, revoke profiles, and reset local state.

## Incident Response Model

Enable safety pause, export redacted evidence, review audit logs, revoke affected profiles, reset demo state, and document the incident without collecting sensitive personal data.

## Legal And Ethical Review

Before alpha pilots, complete legal review, participant consent language, data minimization review, and abuse-prevention review.

## Exit Criteria

- No critical production readiness failures.
- Emulator smoke run recorded.
- Manual VPN permission path validated.
- Release blockers closed or explicitly accepted by owners.
- Production gaps remain documented as gaps.
