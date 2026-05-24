# Evidence Package V2

Evidence Package V2 is a redacted, reviewer-friendly JSON export for the controlled prototype release candidate.

## Schema

Core fields include schema version, generated time, phase, app version, build type, session status, confidence score and status, confidence signals, selected mode, profile audience, applied route scope, blocked route scopes, route policy result, profile expiry, validation results, diagnostics summary, safety pause state, storage mode, safety boundaries, redaction summary, audit event count, operator note, screenshot references, and evidence integrity hash.

## Redaction Rules

Evidence must not contain raw device IDs, raw session IDs, private keys, auth tokens, admin tokens, packet contents, public IP history, contacts, phone numbers, exact location, or raw endpoint secrets.

Evidence includes explicit redaction booleans:

- `no_packet_payload`
- `no_public_ip_history`
- `no_location`
- `no_contacts`
- `no_phone_number`
- `no_automatic_upload`
- `no_public_forwarding`

## Checksum

The evidence hash is SHA-256 over canonical JSON with the hash field cleared before hashing. It is labelled: “Integrity checksum, not cryptographic attestation.”

## Export Flow

The Android Evidence screen supports generating JSON, previewing it, copying it, saving it to app-local storage, sharing through the Android share sheet, and clearing it. Sharing is user initiated only.

## Screenshot References

`screenshotReferences` points to expected Phase 4 screenshot artifact paths under `docs/vpn-product/images/phase4/`. The references support review workflow traceability and do not prove networking behavior.

## Limitations

Evidence V2 is a controlled prototype export. It is not a signed forensic artifact, not an independent attestation, and not proof of production security.
