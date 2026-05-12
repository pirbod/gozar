# Gorz Threat Model

Gorz is not production secure. This threat model documents the risks the PoC is designed to explain, not risks it fully mitigates.

## Content Confidentiality Threat

Message plaintext must remain private from relays, diagnostics, and incident records. The PoC only simulates encryption, so it must not be used for real sensitive communication.

Mitigation in the PoC: mock encrypted envelopes are separated from UI state, and incident records never include message plaintext or raw message content.

## Metadata Exposure Threat

Contact identity, timing, delivery state, and device details can expose sensitive context even when content is protected.

Mitigation in the PoC: incident records avoid real contact identity, phone numbers, exact location, device identifiers, and raw message content.

## Diagnostic Exposure Threat

Connectivity measurements can reveal user environment details or create safety risk if collected too aggressively.

Mitigation in the PoC: diagnostics are simulated, local-first, and never automatically uploaded.

## Network Censorship Ambiguity

A single network signal cannot prove whether a delivery problem is local failure, selective blocking, service outage, domestic-only reachability, or broader loss of external access.

Mitigation in the PoC: the confidence model combines DNS, transport, TLS or QUIC, application delivery, externality, corroboration, and safety penalty signals.

## False Confidence Risk

Overstating delivery confidence can mislead users into trusting a path that is only partially reachable.

Mitigation in the PoC: mandatory delivery layers use a geometric mean and support evidence cannot average away a failed message delivery layer.

## User Safety Risk

Diagnostics and exports can create risk if they reveal too much, happen automatically, or encourage unsafe behavior.

Mitigation in the PoC: safety mode is enabled by default, technical details can be hidden, exports are delayed for review, and emergency pause stops new mock sends.

## Out Of Scope

Gorz does not implement censorship evasion, stealth scanning, hidden probing, bridge discovery, domain fronting, protocol camouflage, or traffic obfuscation.
