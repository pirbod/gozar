# Release Blocker Checklist

Statuses use `PASS`, `FAIL`, `PARTIAL`, or `NOT_STARTED`.

## Safety

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| SAFE-001 | Safety disclaimer remains in README. | PASS | README safety section. | TBD | Block release if removed. |
| SAFE-002 | No public relay discovery is introduced. | PASS | Safety scanners. | TBD | Remove unsafe code or wording. |
| SAFE-003 | No public network probing is introduced. | PASS | Safety scanners. | TBD | Keep diagnostics local or simulated. |
| SAFE-004 | Safety pause remains enforceable. | PARTIAL | Tests cover local pause behavior. | TBD | Add end-to-end alpha validation. |

## Security

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | No obvious secrets are committed. | PASS | Production readiness secret scan. | TBD | Remove and rotate any detected secrets. |
| SEC-002 | Production crypto reviewed. | NOT_STARTED | Gap analysis. | TBD | Commission cryptographic review. |
| SEC-003 | Admin token hardened. | NOT_STARTED | Gap analysis. | TBD | Replace static token with managed auth. |

## Privacy

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| PRIV-001 | No phone number, contacts, or exact location collection. | PASS | Android manifest checker and privacy docs. | TBD | Remove sensitive permissions. |
| PRIV-002 | Evidence exports are redacted. | PARTIAL | Unit tests and docs. | TBD | Add independent redaction review. |
| PRIV-003 | Data retention policy exists. | NOT_STARTED | Gap analysis. | TBD | Define retention and deletion policy. |

## Android

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| ANDROID-001 | Manifest has no sensitive permissions. | PASS | `scripts/check_android_manifest_permissions.py`. | TBD | Remove blocked permissions. |
| ANDROID-002 | No full-device route is added. | PASS | `scripts/check_android_route_safety.py`. | TBD | Keep route policy constrained. |
| ANDROID-003 | Secure settings use Android Keystore. | NOT_STARTED | `PRODUCTION_GAP` comments. | TBD | Replace demo store before alpha. |
| ANDROID-004 | Release signing configured. | NOT_STARTED | Android hardening doc. | TBD | Configure signing and custody. |

## Android Emulator Smoke Test

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| ANDROID-SMOKE-001 | App launches on emulator. | PARTIAL | `GorzSmokeTest.kt`. | TBD | Run managed-device smoke in Android CI. |
| ANDROID-SMOKE-002 | Offline demo flow works. | PARTIAL | Smoke test covers navigation without backend. | TBD | Add emulator artifact evidence. |
| ANDROID-SMOKE-003 | Route policy screen confirms local-only route. | PARTIAL | Smoke test checks route text. | TBD | Run before demo release. |
| ANDROID-SMOKE-004 | Evidence generation shows redaction. | PARTIAL | Smoke test checks redaction wording. | TBD | Add screenshot artifact. |
| ANDROID-SMOKE-005 | Settings screen opens. | PARTIAL | Smoke test checks settings tag. | TBD | Run on CI emulator. |
| ANDROID-SMOKE-006 | VPN permission path manually validated. | NOT_STARTED | Manual checklist. | TBD | Complete Android Studio manual validation. |
| ANDROID-SMOKE-007 | No public forwarding observed. | PARTIAL | UI labels and route check. | TBD | Add manual packet observation evidence. |
| ANDROID-SMOKE-008 | No full-device route observed. | PARTIAL | Route check and manual checklist. | TBD | Record emulator route validation. |

## Backend

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| BACKEND-001 | Safety pause blocks profile issuance. | PASS | Profile API tests. | TBD | Keep regression test required. |
| BACKEND-002 | Revoked and expired profiles fail validation. | PASS | Profile API tests. | TBD | Keep regression test required. |
| BACKEND-003 | Tenant auth model exists. | NOT_STARTED | Gap analysis. | TBD | Design and implement tenant-aware auth. |

## CI/CD

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| CI-001 | Production readiness workflow exists. | PARTIAL | Workflow added. | TBD | Make safety failures required. |
| CI-002 | Android emulator smoke stable. | PARTIAL | Manual/nightly workflow. | TBD | Promote after stability data. |
| CI-003 | Dependency audits run. | PARTIAL | Best-effort workflow. | TBD | Pin audit tools and fail critical findings. |

## Documentation

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| DOC-001 | Product overview exists. | PASS | `docs/product/one-page-overview.md`. | TBD | Keep current with architecture. |
| DOC-002 | Gap analysis exists. | PASS | `docs/product/production-gap-analysis.md`. | TBD | Review each release. |
| DOC-003 | Runbooks exist. | PASS | Operations docs. | TBD | Validate during demos. |

## Operations

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| OPS-001 | Local demo runbook exists. | PASS | `docs/operations/runbook-local-demo.md`. | TBD | Dry run before demos. |
| OPS-002 | Incident runbook exists. | PASS | `docs/operations/incident-response-runbook.md`. | TBD | Exercise with safety pause. |
| OPS-003 | Observability baseline exists. | PARTIAL | `observability/README.md`. | TBD | Add metrics and alerting plan. |

## Compliance

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| COMP-001 | Legal review completed. | NOT_STARTED | Gap analysis. | TBD | Complete legal review before pilots. |
| COMP-002 | Abuse-prevention review completed. | NOT_STARTED | Risk register. | TBD | Define abuse handling process. |

## Demo Readiness

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| DEMO-001 | Safe demo script exists. | PASS | Demo positioning and Phase 3 script. | TBD | Keep wording constrained. |
| DEMO-002 | Screenshots exist. | PASS | Phase 3 SVG screenshots. | TBD | Refresh after UI changes. |

## Release Readiness

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| REL-001 | Version is set. | PARTIAL | `VERSION`. | TBD | Align release tags and changelog. |
| REL-002 | Changelog exists. | PASS | `CHANGELOG.md`. | TBD | Update for every release. |
| REL-003 | All blockers closed. | NOT_STARTED | This checklist. | TBD | Close every FAIL/PARTIAL/NOT_STARTED item before production release. |
