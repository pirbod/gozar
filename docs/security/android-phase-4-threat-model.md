# Android Phase 4 Threat Model

## Assets

Demo profile material, local settings, audit history, evidence JSON, screenshot artifacts, Profile API admin token, local packet counters, and release artifacts.

## Trust Boundaries

Android app storage, Android Keystore experimental path, local Profile API, app-local evidence export, Android share sheet, emulator CI, and repository release artifacts.

## Actors

Demo operator, reviewer, developer, local device user, CI runner, and a user who mistakes the prototype for a finished product.

## Abuse Cases And Misuse Risks

Risks include release artifact misuse, screenshot leakage, admin token leakage, evidence export sharing outside the review group, and demo claims being interpreted too broadly.

## Android-Specific Risks

Sensitive permission creep, route guard regression, VPN permission confusion, packet counter misunderstanding, and emulator-only validation blind spots.

## Storage Risks

Demo storage is default and not suitable for production secrets. Android Keystore storage is experimental until tested across key invalidation, backup, restore, and migration scenarios.

## Profile API Risks

The API remains local-first with static admin token limitations, local tenant assumptions, and no production auth model.

## Evidence, Diagnostics, Route, Screenshot, CI/CD, And Supply-Chain Risks

Evidence can leak context if shared carelessly. Diagnostics must remain local-only. Route policy must continue blocking unsafe scopes. Screenshots can reveal local state. CI artifacts can expose debug builds. Dependencies require audit before any production expansion.

## Controls

Route guard tests, manifest permission checks, safety wording checks, local-only diagnostics, evidence redaction tests, release checklist, threat model, privacy review, and production readiness report.

## Residual Risks

Independent review, signing, tenant auth, retention policy, production crypto review, and stable emulator CI remain gaps.

## Go/No-Go Criteria

Demo-ready requires safety checks, docs, manifest, and honest skipped reports where tooling is unavailable. Production readiness remains NOT_READY.
