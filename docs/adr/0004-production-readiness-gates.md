# ADR 0004: Production Readiness Gates For Controlled Alpha

## Status

Accepted

## Context

Gozar/Gorz is moving from research prototype toward demo-ready alpha governance while remaining a controlled prototype. Reviewers need deterministic local reports, safety gates, and release blockers without implying production readiness.

## Decision

Add `make production-readiness-check` as the repository-level readiness entry point. The command generates JSON and Markdown reports, checks safety wording, Android permissions, Android route safety, backend safety, docs completeness, CI assets, release blockers, and documented production gaps.

## Consequences

- Critical safety issues fail local and CI checks.
- Missing production controls are reported honestly as warnings or gaps.
- Runtime reports become a standard validation artifact.
- The project remains not production secure until release blockers are closed.
