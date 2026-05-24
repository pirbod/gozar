# Release Blocker Checklist

Statuses use `PASS`, `PARTIAL`, `SKIPPED`, `FAIL`, or `NOT_STARTED`.

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

## Phase 4 Controlled Release Readiness

| ID | Requirement | Status | Evidence | Owner | Remediation |
| --- | --- | --- | --- | --- | --- |
| PHASE4-ROADMAP-001 | Four-phase roadmap documented. | PASS | `docs/product/four-phase-roadmap.md`. | TBD | Keep closure statement current. |
| PHASE4-ANDROID-001 | App builds. | SKIPPED | Requires local Gradle/Android SDK in this shell. | TBD | Run Android Studio or CI build. |
| PHASE4-ANDROID-002 | Manifest has no sensitive permissions. | PASS | Manifest checker. | TBD | Remove blocked permissions. |
| PHASE4-ROUTE-001 | No full-device IPv4 route. | PASS | Route checker and route guard tests. | TBD | Block release on regression. |
| PHASE4-ROUTE-002 | No full-device IPv6 route. | PASS | Route guard tests. | TBD | Block release on regression. |
| PHASE4-ROUTE-003 | Route guard tests pass. | SKIPPED | Gradle unavailable locally. | TBD | Run Android tests in Android Studio or CI. |
| PHASE4-CONFIDENCE-001 | Confidence engine tests pass. | SKIPPED | Gradle unavailable locally. | TBD | Run Android tests in Android Studio or CI. |
| PHASE4-EVIDENCE-001 | Evidence Package V2 generated. | PARTIAL | Code and tests added. | TBD | Verify on emulator. |
| PHASE4-EVIDENCE-002 | Evidence redaction tests pass. | SKIPPED | Gradle unavailable locally. | TBD | Run Android tests in Android Studio or CI. |
| PHASE4-EVIDENCE-003 | Integrity checksum present. | PASS | Evidence repository code and UI label. | TBD | Verify generated JSON. |
| PHASE4-DIAG-001 | Diagnostics local-only. | PASS | Diagnostics use case blocks non-local endpoints. | TBD | Keep scanner coverage. |
| PHASE4-PAUSE-001 | Safety pause blocks connect. | PARTIAL | Use case and UI wired. | TBD | Verify on emulator. |
| PHASE4-STORAGE-001 | Storage mode visible. | PASS | Settings screen. | TBD | Keep visible in screenshots. |
| PHASE4-STORAGE-002 | Keystore gap documented. | PASS | Settings UI and gap docs. | TBD | Complete hardening before pilot. |
| PHASE4-EMULATOR-001 | Emulator smoke passes or skipped with reason. | PARTIAL | Report script added. | TBD | Run with emulator. |
| PHASE4-SCREENSHOT-001 | Screenshots captured or skipped with reason. | PARTIAL | Screenshot script added. | TBD | Capture final screenshots. |
| PHASE4-DOCS-001 | Threat model exists. | PASS | `docs/security/android-phase-4-threat-model.md`. | TBD | Review findings. |
| PHASE4-DOCS-002 | Privacy review exists. | PASS | `docs/privacy/android-phase-4-privacy-review.md`. | TBD | Review findings. |
| PHASE4-DOCS-003 | Final validation report exists. | PASS | `docs/vpn-product/phase-4-final-validation-report.md`. | TBD | Fill environment placeholders. |
| PHASE4-RELEASE-001 | Release candidate manifest exists. | PARTIAL | Generator added. | TBD | Generate runtime report. |
| PHASE4-README-001 | README updated. | PASS | README Phase 4 section. | TBD | Keep commands current. |
| PHASE4-FINAL-001 | Controlled release candidate decision documented. | PASS | Final validation report. | TBD | Update after final checks. |
| PHASE4-PLATFORM-001 | Terraform layer exists and reports validation status. | PARTIAL | `infra/terraform/` and runtime report. | TBD | Run with Terraform installed. |
| PHASE4-PLATFORM-002 | Kubernetes manifests exist and report validation status. | PARTIAL | `deploy/kubernetes/` and runtime report. | TBD | Run with kubectl installed. |
| PHASE4-OBS-001 | Prometheus and Grafana assets exist. | PASS | `observability/`. | TBD | Run local dashboard capture. |
| PHASE4-DETECT-001 | SIEM-style detection report generated. | PASS | `runtime/reports/siem-detection-report.md`. | TBD | Keep sample events updated. |
| PHASE4-AI-001 | Deterministic incident summary demo generated. | PASS | `runtime/reports/incident-summary.md`. | TBD | Review summary wording. |
| PHASE4-VIDEO-001 | Demo video script and placeholder exist. | PASS | `docs/demo/`. | TBD | Record final video when emulator and desktop capture are available. |

Production readiness must not be marked PASS for Phase 4.
