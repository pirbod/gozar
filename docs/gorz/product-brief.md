# Gorz Product Brief

Gorz is a local-first private messaging prototype inspired by the Gozar research model. It presents
message delivery as a confidence-aware evidence state rather than a simple sent or failed label.

## Purpose

Gorz helps reviewers explore how a messaging UI can explain uncertain delivery using local demo
evidence. It shows identities, conversations, redacted envelope records, confidence scoring,
incident export, audit history, and emergency pause.

## User Personas

- Stakeholder reviewing a clickable local messaging demo.
- Safety-conscious reviewer checking diagnostic boundaries.
- Research reviewer evaluating confidence-scored delivery language.
- Product designer exploring delivery-state UX under uncertainty.

## Use Cases

- Create local demo identities.
- Send local demo messages under multiple scenarios.
- Compare confidence-scored delivery status.
- Inspect evidence behind the score.
- Export a redacted incident package.
- Review audit events.
- Enable emergency pause.

## Demo Narrative

1. Create two demo identities.
2. Create a local conversation.
3. Send a `direct_ok` message.
4. Send a `degraded` message.
5. Send a `blocked` message.
6. Compare the confidence cards and evidence breakdown.
7. Generate and download a redacted incident package.
8. Review audit history.
9. Enable emergency pause and verify sends are blocked.

## Product Boundaries

Gorz is a prototype, a local demo, and not for real sensitive communication. It does not implement
production secure messaging, external probing, bridge discovery, relay discovery, public network
scanning, exact location collection, phone number collection, or automatic diagnostic upload.

## Roadmap

- Keep the prototype local-first and safe by default.
- Replace demo cryptography only after a formal production security plan exists.
- Add richer local-only evidence review tools.
- Add controlled lab allowlists only if explicitly documented and enabled.

