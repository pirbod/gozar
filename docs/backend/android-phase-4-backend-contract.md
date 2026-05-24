# Android Phase 4 Backend Contract

## Endpoints Used By Android

- `GET /api/profile/health`
- `GET /api/profile/mobile/bootstrap`
- `POST /api/profile/devices/register`
- `POST /api/profile/profiles`
- `GET /api/profile/profiles/{profile_id}/validate`
- safety pause admin endpoints for local demo operation

## Request Fields

Android sends demo device key material, selected demo mode, stored demo device ID when available, and local admin token for admin-only safety operations.

## Response Fields

The app expects profile ID, audience, issued time, expiry, TTL, safety notes, policy reasons, encrypted demo payload, signature, validation status, revocation checks, and mobile bootstrap safety notes.

## Safety Notes

Responses must continue to state local-only boundaries, no full-device route, no public forwarding, and no public probing.

## Auth Limitations

Admin token handling is local-demo only. Tenant-aware auth, scoped user identity, secret rotation, rate limits, and production audit accountability remain gaps.

## Local-Only Assumptions

Android emulator uses `http://10.0.2.2:8095`. Offline fallback uses deterministic local demo profiles.

## Audit Redaction Behavior

Audit export must redact sensitive identifiers and avoid tokens, keys, and packet contents.

## Backend-Connected Demo Flow

The app checks health, loads bootstrap, registers device, requests profile, verifies signature, decrypts the demo payload, validates profile state, and starts local lifecycle.

## Offline Fallback Flow

If the local backend is unavailable or offline mode is selected, Android uses local deterministic profiles and labels the mode clearly.

## Non-Goals

Phase 4 does not implement production tenant auth, public network probing, relay registry, production gateway logic, or real public VPN functionality.
