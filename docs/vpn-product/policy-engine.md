# Policy Engine

The Phase 1 policy engine is deterministic and conservative. It consumes device capabilities, requested mode, risk tolerance, client context, safety state, and optional diagnostic scenario.

## Rules

- Safety pause returns `no_profile`.
- `demo_messaging_only` selects `quic_like_demo`.
- Android or iOS devices that support WireGuard-like profiles can receive `wireguard_like_demo`, with a note that real OS integration is future work.
- `degraded` previous failures select `quic_like_demo`.
- `blocked` previous failures return `no_profile`.
- Low risk tolerance keeps routing in `demo_split_tunnel`.
- Unknown platforms fall back to `quic_like_demo`.

## Outputs

The policy result includes selected profile type, decision, confidence, risk, reasons, policy version, and safety notes. The issuer can only use the bounded local templates in `profile_templates.py`.

