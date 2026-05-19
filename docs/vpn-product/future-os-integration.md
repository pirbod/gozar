# Future OS Integration

Future OS integration is explicitly not implemented in Phase 1.

Potential future work includes:

- iOS and macOS NetworkExtension and Personal VPN configuration management.
- Android VpnService integration.
- Desktop WireGuard client integration.
- User consent and revocation UX.
- App store compliance review.
- Independent security audit.
- Legal review.
- KMS, secure enclave, or HSM-backed issuer keys.
- Production key management review.

Future adapters should consume already-issued signed encrypted profile envelopes. They should not let diagnostics directly generate arbitrary configs, and they should keep consent, revocation, and audit redaction as first-class requirements.
