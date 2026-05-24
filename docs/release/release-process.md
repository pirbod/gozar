# Release Process

## Versioning Strategy

Use semantic pre-release versions for alpha work, for example `0.4.0-alpha`.

## Pre-Release Checklist

- Run `make production-readiness-check`.
- Run language-specific tests.
- Run Android smoke test or document why it was skipped.
- Review release blocker checklist.

## Safety Review

Confirm README safety disclaimer, no unsafe Android route, no sensitive Android permission, no public probing, and no automatic diagnostic upload.

## CI Requirements

CI must run safety scanners, backend tests, Android static checks, and production readiness report generation.

## Docs Requirements

Update changelog, release notes, risk register, gap analysis, and validation report.

## Artifact Generation

Generate runtime reports and attach relevant validation artifacts.

## Homebrew Formula Update Process

Update formula metadata after tags are created, then run the Homebrew formula check.

## Android Release Gap

Android release signing and Play distribution are not configured. This remains a release blocker for any real alpha distribution.

## Rollback Plan

Keep prior release tag, revert the release commit if needed, disable demo services, and publish corrected release notes.
# Phase 4 Controlled Release Candidate Addendum

For `0.4.0-rc1`, use `docs/release/phase-4-controlled-release-process.md`. Required artifacts are the final validation report, production readiness report, screenshot report, emulator smoke report, release candidate manifest, privacy review, threat model, backend contract, release notes, and updated blocker checklist.
