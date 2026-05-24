# Production Readiness Threat Model

## Assets

- Demo profile envelopes.
- Local admin tokens.
- Android local identity.
- Audit logs.
- Redacted evidence packages.
- Evaluation reports.
- CI secrets and release artifacts.

## Trust Boundaries

- Android app storage.
- Local API services.
- Docker runtime.
- GitHub Actions.
- Operator workstation.

## Actors

- Demo operator.
- Internal reviewer.
- Academic collaborator.
- Accidental misuser.
- Malicious contributor.
- Supply-chain attacker.

## Abuse Cases

- Misrepresenting the prototype as a production VPN.
- Introducing unsafe route additions.
- Adding sensitive mobile permissions.
- Expanding diagnostics into public probing.
- Committing secrets.
- Weakening safety pause.

## Misuse Risks

The primary misuse risk is overclaiming or repurposing the prototype outside controlled environments. Safety wording, docs, and CI scanners reduce but do not eliminate this risk.

## Android Risks

- Permission creep.
- Demo storage mistaken for secure storage.
- VPN lifecycle mistaken for traffic forwarding.
- Emulator tests not covering device-specific issues.

## Backend Risks

- Static admin token.
- No tenant auth.
- SQLite-only storage.
- Insufficient rate limiting.
- Local demo secrets.

## CI/CD Risks

- Emulator instability.
- Dependency audit gaps.
- Workflow drift.
- Artifact signing gaps.

## Supply-Chain Risks

- npm, Cargo, Python, Gradle, and GitHub Action dependencies can introduce vulnerabilities.
- Best-effort audits are not a substitute for pinned release governance.

## Controls

- Production readiness report.
- Android route and permission checks.
- Backend safety scanner.
- Safety wording scanner.
- Secret pattern scanner.
- Release blocker checklist.
- Risk register.

## Open Risks

- Independent audit not complete.
- Legal review not complete.
- Production crypto not implemented.
- Tenant auth not implemented.
- Release signing not configured.
