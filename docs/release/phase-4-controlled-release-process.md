# Phase 4 Controlled Release Process

## Scope

Phase 4 produces a controlled release candidate for demo, research, security review, company evaluation, academic review, and stakeholder presentation.

## Non-Goals

This release does not create a production VPN, public routing product, secure messenger, or production-secure communication product.

## Build Process

Run:

```bash
make phase4-check
make release-candidate-manifest
```

If Android Gradle tooling is unavailable, reports must say SKIPPED rather than PASS.

## Screenshot Requirement

Run `make phase4-screenshots` or follow the manual screenshot guide. Missing screenshots must be reported honestly.

## Validation Report Requirement

`docs/vpn-product/phase-4-final-validation-report.md` is the final roadmap validation report and references generated runtime reports.

## Artifact Manifest And Checksum

`runtime/reports/gorz-android-rc-manifest.json` and `.md` record version, commit SHA, APK state, checksum when APK exists, screenshot status, smoke status, known gaps, and release decision.

## Reviews

Safety review, privacy review, threat model review, release blocker checklist, and production readiness report must be present before sharing the candidate.

## Rollback

Rollback is operational: stop distribution of the debug artifact, revoke local demo profiles when applicable, clear local app data, and archive reports from the failed candidate.

## No Production Claims

All release notes and demos must keep controlled prototype language and production readiness set to NOT_READY.
