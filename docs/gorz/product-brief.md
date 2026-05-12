# Gorz Product Brief

Gorz is a privacy-first encrypted messaging proof of concept inspired by the Gozar research framework for confidence-scored, multi-layer Internet access evidence. It presents message delivery as an understandable confidence state instead of leaving users in an indefinite connecting state.

## Purpose

Gorz helps a user understand whether a mock encrypted message appears deliverable, delayed, queued, likely blocked, failed, or inconclusive. It does this with local simulated evidence across DNS, transport, TLS or QUIC, message delivery, externality, corroboration, and safety minimization.

## User Personas

- Everyday private messenger user who needs clear delivery status.
- Safety-conscious user who wants minimal diagnostics and no automatic upload.
- Research reviewer evaluating how confidence-scored network evidence can be made understandable.
- Product designer exploring messaging UX under uncertain network conditions.

## Use Cases

- Send a one-to-one mock encrypted message.
- Compare delivery state across safe simulated network scenarios.
- Review a compact confidence panel without raw technical detail.
- Enable safety controls such as local diagnostics only and emergency pause.
- Generate a redacted incident record preview for review.

## Demo Narrative

1. Gorz opens to a direct chat with Sara.
2. Safety mode is enabled by default.
3. The user sends a mock encrypted message.
4. The selected network scenario determines whether the message is delivered, queued, delayed, likely blocked, or failed.
5. The network confidence panel explains the result using high-level language.
6. The incident panel shows redacted JSON with no real identifiers or message plaintext.

## Product Boundaries

Gorz does not implement censorship evasion, hidden probing, protocol camouflage, bridge discovery, domain fronting, or automatic diagnostic upload. All diagnostic evidence is simulated and local to the PoC.

## Roadmap

- Phase 1: Real UI and mock local encryption.
- Phase 2: Replace mock crypto with audited E2EE library.
- Phase 3: Add real backend relay with encrypted envelopes only.
- Phase 4: Add optional privacy-preserving aggregate diagnostics.
- Phase 5: Add formal incident export compatible with Gozar evidence schemas.
- Phase 6: Add independent third-party audit.
