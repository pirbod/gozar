# Gorz Architecture

Gorz is implemented as `ts/apps/gorz-web`, a Vite React and TypeScript workspace. The first PoC is frontend-only and has no backend dependency.

## Frontend Modules

- `src/App.tsx` coordinates selected conversation, selected diagnostic scenario, safety controls, message state, confidence results, and incident preview.
- `src/components` contains small typed React components for chat, delivery state, network confidence, safety mode, incident export, and settings.
- `src/data` contains safe mock contacts, conversations, messages, and network events.
- `src/types` defines chat, connectivity, and incident record contracts.
- `src/utils` contains small formatting and ID helpers.

## Mock Crypto

`src/crypto/mockE2EE.ts` contains demo-only functions:

- `generateMockIdentityKey()`
- `deriveMockSessionKey()`
- `encryptMessageMock()`
- `decryptMessageMock()`
- `generateSafetyNumber()`
- `verifySafetyNumberMock()`

Each function is explicitly documented as a PoC mock that must be replaced with audited cryptographic libraries before production. The mock encrypted envelope is only for UI and state-flow demonstration.

## Connectivity Engine

`src/connectivity/confidenceModel.ts` implements a bottleneck-aware scoring model based on the Gozar methodology:

```text
mandatoryScore = geometric mean of DNS, transport, TLS/QUIC, and application delivery
supportScore = weighted average of externality and corroboration
overall = clamp((mandatoryScore ** 0.7) * (supportScore ** 0.3) * (1 - safetyPenalty), 0, 1)
```

This prevents one failed mandatory layer from being averaged away by unrelated support signals.

## Diagnostic Simulator

`src/connectivity/diagnosticSimulator.ts` supplies local mock scenarios:

- Normal Internet access
- App relay blocked
- DNS interference
- TLS handshake failure
- Domestic-only connectivity
- General outage
- Intermittent mobile disruption
- QUIC degraded but TCP available
- Application delivery failure
- Low evidence, inconclusive

The simulator does not run real probes or make requests to external destinations.

## Incident Records

`src/connectivity/incidentRecord.ts` generates a redacted JSON record with confidence score, layer scores, delivery state, safety controls, redactions, and notes. It intentionally excludes real IP addresses, phone numbers, exact GPS locations, contact identities, message plaintext, raw message content, and device identifiers.

## Future Backend Integration

A production architecture would need audited E2EE, durable local storage, account recovery decisions, key verification UX, encrypted envelope relay behavior, abuse-resistant rate limits, privacy-preserving aggregate diagnostics, and independent security review. These are roadmap items and are not implemented in the PoC.
