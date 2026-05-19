# Threat Model

## Assets

- Device public key hash.
- Issuer public key.
- Signed encrypted profile envelope.
- Short-lived simulated profile payload.
- Revocation state.
- Redacted audit evidence.

## Trust Boundaries

- The demo client holds the device private key locally.
- The Profile API receives only the device public key.
- SQLite stores local metadata, not plaintext profile payloads.
- Audit export is treated as shareable evidence only after redaction.

## Attacker Assumptions

- A local developer may inspect API responses, database rows, and logs.
- A malformed client may request invalid device or profile identifiers.
- A stale client may try to validate expired or revoked profiles.
- A caller may try to include sensitive fields in audit metadata.

## Out Of Scope

- Production VPN security.
- OS VPN profile installation.
- Public gateway operation.
- Public network probing.
- Endpoint scraping.
- iOS, macOS, Android, or desktop tunnel adapters.
- Protection for real sensitive communication.

## Misuse Risks

- Treating simulated profile payloads as production secure.
- Logging decrypted payloads during local debugging.
- Expanding diagnostics into public network behavior before safety review.
- Allowing arbitrary config generation instead of bounded templates.

## Safety Controls

- Safety pause blocks new profile issuance.
- Blocked local scenarios return `no_profile`.
- Payloads are encrypted before returning to the client.
- Envelopes are signed with canonical JSON.
- Audit records hash identifiers and remove profile payload material.
- The API returns metadata only for stored profiles.

