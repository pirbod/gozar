# Gorz Safety Model

Gorz treats user safety as a primary product requirement. The PoC demonstrates safety-aware defaults without running real diagnostics.

## Minimum Exposure

The app shows high-level delivery confidence by default and keeps raw technical detail behind an advanced toggle. Safety mode can hide the advanced view.

## Local-First Diagnostics

All diagnostic evidence is simulated locally. The PoC does not make real requests to censorship-sensitive destinations and does not perform live network probing.

## No Automatic Upload

Diagnostic upload is disabled by default. Incident records are generated locally and must be intentionally copied or downloaded by the user.

## No Raw IP Collection

Incident records are designed to exclude real IP addresses, phone numbers, exact GPS location, device identifiers, real contact identity, message plaintext, and raw message content.

## Redaction

The incident record generator includes an explicit redaction list so reviewers can see what has been excluded. Redactions are part of the exported JSON.

## Delayed Release

The safety controls include delayed incident export, keeping review before sharing as the default flow.

## Emergency Pause

Emergency pause disables new mock message sends. Existing local messages remain visible, but the composer is disabled until the pause is lifted.

## Safety Copy

The app states: “Gorz prioritizes user safety. Diagnostics are minimized, local-first, and never automatically uploaded in this PoC.”
