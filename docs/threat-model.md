# Threat Model

## Scope

`gozar` is a local research prototype for lawful experimentation. The threat model is intended to make the demo safer and more honest about what it does not solve.

## Assets

- Integrity of control-plane path decisions
- Availability of overlay forwarding capacity
- Visibility into per-hop queue pressure
- Local user intent when sending traffic through the desktop edge client

## Adversaries Considered

- A local or adjacent actor attempting to inject forged control-plane messages
- A remote peer causing queue exhaustion on a relay or gateway
- An operator or tester accidentally leaving the system in an unexpected path mode
- Benign failures on the direct path that should trigger a safer alternate route

## Mitigations In This Prototype

- Control-plane messages are authenticated with an HMAC signature and nonce-bound response envelope.
- Every forwarding hop has a bounded in-flight queue.
- The desktop client can switch away from the active path on runtime failure.
- Returned route metadata makes hop choice and queue depth visible during testing.
- The demo target is a local echo service rather than an unrestricted network forwarder.

## Explicitly Out Of Scope

- Production identity, PKI, certificate rotation, or hardware-backed secrets
- Traffic obfuscation, censorship bypass guarantees, or stealth behavior
- Endpoint hardening, sandboxing, device posture, or kernel tunnel integration
- Formal anonymity properties
- Automatic NAT traversal, roaming, or wide-area path measurement

## Risks And Caveats

- The demo uses development-only QUIC trust assumptions.
- A shared secret is convenient for local runs but not sufficient for production.
- Queue limits are count-based rather than byte-based, so they are only a first approximation of flow control.
- The control plane stores node state in memory only and has no audit trail.

## Next Security Steps

- Replace the shared secret with per-node credentials and key rotation.
- Add mutual authentication for dataplane sessions.
- Enforce freshness windows and replay caches on control messages.
- Expand queue accounting from request counts to stream and byte windows.
- Add structured audit logging and persistent control-plane state.

