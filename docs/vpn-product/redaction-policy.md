# Redaction Policy

Audit entries are designed to support privacy-preserving diagnostics for the local profile lifecycle.

## Removed Or Hashed

- Plaintext profile payloads.
- Private keys.
- Raw device public keys.
- Device identifiers.
- Exact IP addresses.
- User location.
- Encrypted payload bytes.
- Raw signatures.
- Local endpoint strings from simulated templates.

## Export Metadata

Audit export includes a redaction block:

```json
{
  "plaintext_profile_removed": true,
  "private_keys_removed": true,
  "device_public_keys_removed": true,
  "encrypted_payload_replaced_with_hash": true,
  "signature_replaced_with_hash": true,
  "device_ids_hashed": true,
  "timestamps_bucketed": true,
  "local_endpoints_removed": true
}
```

Export timestamps are bucketed by hour. Device and profile identifiers inside metadata are hashed before storage.

Audit export may include safe evidence such as `envelope_hash`, `encrypted_payload_hash`, `signature_hash`, `issuer_key_id`, profile type, policy version, TTL, status, and safety notes.
