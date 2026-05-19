# Future iOS Plan

Phase 2 does not implement iOS. iOS remains documentation-only until the Android local VPN lifecycle prototype and Profile API hardening are stable.

Future iOS work would require:

- Swift app prototype.
- Apple NetworkExtension entitlement review.
- `NEPacketTunnelProvider` implementation.
- Keychain and Secure Enclave evaluation.
- Explicit user consent flows.
- App Store review planning.
- Platform privacy review.
- Short-lived adaptive session profile validation.
- Revocation checks before tunnel startup.
- Clear UI language that the prototype is not production secure and not for real sensitive communication.

Any iOS implementation must preserve the same safety boundaries: no public gateway, no public network probing, and no public relay discovery.
