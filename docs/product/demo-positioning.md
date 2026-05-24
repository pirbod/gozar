# Demo Positioning

## 30-Second Pitch

Gozar/Gorz is a controlled research prototype for studying confidence-aware access and messaging flows. It shows adaptive profile decisions, local lifecycle validation, redacted evidence, and safety pause controls without claiming production routing or real secure communication.

## 2-Minute Pitch

The repo combines Gozar Core for research overlay and path scoring, Gorz Web for confidence-aware messaging, Profile API for short-lived adaptive profiles, Gorz Android for mobile UX and local VPN lifecycle validation, and Evaluation for controlled lab evidence. The value is governance and testability: reviewers can see safety boundaries, route policy, confidence signals, audit events, and redacted evidence in one platform.

## 5-Minute Technical Pitch

Profile API issues short-lived signed encrypted demo profiles, validates TTL and revocation, and exports redacted audit evidence. Gorz Android uses that profile or an offline deterministic fallback to demonstrate onboarding, connection stages, confidence scoring, route-policy explanation, diagnostics, evidence, audit, and safety pause. Gozar Core and Evaluation provide the controlled research substrate for path scoring. The system is intentionally constrained to local environments and demo-only cryptography.

## Safe Wording

- Controlled prototype.
- Local lifecycle only.
- Confidence-aware demo.
- Redacted evidence.
- Simulated diagnostics.
- Not production secure.
- Not a public routing product.

## Forbidden Wording

- Unblock.
- Bypass.
- Stealth.
- Guaranteed access.
- Production secure.
- Field-deployable VPN.
- Claims that the system cannot be detected.

## FAQ

### Is this a production VPN?

No. It is a controlled research prototype and Android local lifecycle demo.

### Does it forward public traffic?

No. Android packets may be counted for local diagnostics and are dropped.

### Does it collect sensitive mobile data?

No. The Android manifest avoids contacts, phone, audio, camera, and location permissions.

### Can it run without the backend?

Yes. Phase 3 includes offline demo mode with deterministic local data.

## Reviewer Objections And Answers

| Objection | Answer |
| --- | --- |
| This looks like a production VPN. | The UI and docs explicitly label it controlled prototype and local lifecycle only. |
| Demo crypto could be mistaken for real crypto. | Gap analysis and docs mark demo crypto as non-production. |
| Diagnostics could expand too far. | Safety scanners block public probing language and route changes. |
| Android emulator CI is fragile. | Smoke test is small, deterministic, and can run manual/nightly until stable. |
