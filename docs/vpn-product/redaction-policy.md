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

## Export Metadata

Audit export includes a redaction block:

```json
{
  "plaintext_profile_removed": true,
  "private_keys_removed": true,
  "device_ids_hashed": true,
  "timestamps_bucketed": true
}
```

Export timestamps are bucketed by hour. Device and profile identifiers inside metadata are hashed before storage.

