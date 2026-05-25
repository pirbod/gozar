# Gozar/Gorz Production Readiness Report

Generated: 2026-05-24T20:30:23.537753+00:00

## Summary

- Overall: PARTIAL
- Controlled release readiness: PASS
- Controlled release evidence: PARTIAL
- Platform readiness: PARTIAL
- Production readiness report: READY
- Production-ready for real use: NO
- Production security claim: NO
- Critical failures: 0
- Warnings: 11
- Skipped: 3

## Checks

## Platform Readiness

| Area | Status |
| --- | --- |
| Terraform | PARTIAL |
| Kubernetes | PARTIAL |
| Observability | PASS |
| SIEM detection | PASS |
| Incident summaries | PASS |
| GitHub Actions | PASS |
| README | PASS |
| Screenshots | PARTIAL |
| Demo video | PARTIAL |

## Phase 4 Controlled Release Readiness

| Area | Status |
| --- | --- |
| Roadmap closure | Evaluated below |
| Android hardening | Evaluated below |
| Storage readiness | Evaluated below |
| Route safety | Evaluated below |
| Confidence engine | Evaluated below |
| Evidence package | Evaluated below |
| Diagnostics | Evaluated below |
| Safety pause | Evaluated below |
| Emulator smoke | Evaluated below |
| Screenshot evidence | Evaluated below |
| Release artifact manifest | Evaluated below |
| Privacy review | Evaluated below |
| Threat model | Evaluated below |
| Backend contract | Evaluated below |
| Documentation | Evaluated below |
| Controlled release readiness | PASS |
| Controlled release evidence | PARTIAL |
| Production readiness report | READY |
| Production-ready for real use | NO |

| Status | Check | Detail | Remediation |
| --- | --- | --- | --- |
| PASS | README exists | README.md | Create README.md. |
| PASS | README safety wording present | Found 'Safety Disclaimer' | Restore the README safety disclaimer. |
| PASS | README contains not a circumvention tool | Found 'not a circumvention tool' | Restore the project positioning disclaimer. |
| PASS | README contains not a field-deployment routing product | Found 'not a field-deployment routing product' | Restore the project positioning disclaimer. |
| PASS | Safety boundaries doc exists | docs/safety-boundaries.md | Create docs/safety-boundaries.md. |
| PASS | Production gap analysis exists | docs/product/production-gap-analysis.md | Create docs/product/production-gap-analysis.md. |
| PASS | Release blocker checklist exists | docs/product/release-blocker-checklist.md | Create docs/product/release-blocker-checklist.md. |
| PASS | Risk register exists | docs/product/risk-register.md | Create docs/product/risk-register.md. |
| PASS | Phase 1 docs exist | docs/vpn-product/phase-1-local-profile-lifecycle.md | Create docs/vpn-product/phase-1-local-profile-lifecycle.md. |
| PASS | Phase 2 docs exist | docs/vpn-product/phase-2-android-vpnservice.md | Create docs/vpn-product/phase-2-android-vpnservice.md. |
| PASS | Phase 3 docs exist | docs/vpn-product/phase-3-android-clickable-prototype.md | Create docs/vpn-product/phase-3-android-clickable-prototype.md. |
| PASS | AndroidManifest.xml does not include ACCESS_FINE_LOCATION | Checked for 'ACCESS_FINE_LOCATION' | Remove 'ACCESS_FINE_LOCATION'. |
| PASS | AndroidManifest.xml does not include ACCESS_COARSE_LOCATION | Checked for 'ACCESS_COARSE_LOCATION' | Remove 'ACCESS_COARSE_LOCATION'. |
| PASS | AndroidManifest.xml does not include READ_CONTACTS | Checked for 'READ_CONTACTS' | Remove 'READ_CONTACTS'. |
| PASS | AndroidManifest.xml does not include READ_PHONE_NUMBERS | Checked for 'READ_PHONE_NUMBERS' | Remove 'READ_PHONE_NUMBERS'. |
| PASS | AndroidManifest.xml does not include READ_PHONE_STATE | Checked for 'READ_PHONE_STATE' | Remove 'READ_PHONE_STATE'. |
| PASS | Android does not add 0.0.0.0/0 route | Checked for 'addRoute("0.0.0.0"' | Remove 'addRoute("0.0.0.0"'. |
| PASS | Android does not add ::/0 route | Checked for 'addRoute("::"' | Remove 'addRoute("::"'. |
| PASS | Android code has no public relay discovery strings | Checked phrase 'public relay discovery' | Remove unsafe phrase 'public relay discovery'. |
| PASS | Android code has no public gateway discovery strings | Checked phrase 'public gateway discovery' | Remove unsafe phrase 'public gateway discovery'. |
| PASS | Android code has no bridge discovery strings | Checked phrase 'bridge discovery' | Remove unsafe phrase 'bridge discovery'. |
| PASS | Android code has no external probing strings | Checked phrase 'external probing' | Remove unsafe phrase 'external probing'. |
| PASS | Android code has no automatic diagnostic upload strings | Checked phrase 'automatic diagnostic upload' | Remove unsafe phrase 'automatic diagnostic upload'. |
| PASS | Python code has no public relay discovery strings | Checked phrase 'public relay discovery' | Remove unsafe phrase 'public relay discovery'. |
| PASS | Python code has no public gateway discovery strings | Checked phrase 'public gateway discovery' | Remove unsafe phrase 'public gateway discovery'. |
| PASS | TypeScript code has no public relay discovery strings | Checked phrase 'public relay discovery' | Remove unsafe phrase 'public relay discovery'. |
| PASS | Rust code has no public relay discovery strings | Checked phrase 'public relay discovery' | Remove unsafe phrase 'public relay discovery'. |
| PASS | Phase 3 safety checker exists | scripts/check_phase3_safety.py | Create scripts/check_phase3_safety.py. |
| PASS | Makefile android-check target exists | Found '\nandroid-check:' |  |
| PASS | Makefile phase2-check target exists | Found '\nphase2-check:' |  |
| PASS | Makefile phase3-check target exists | Found '\nphase3-check:' |  |
| PASS | GitHub Actions workflow exists | .github/workflows/ci.yml | Create .github/workflows/ci.yml. |
| PASS | Docker compose files exist | docker-compose.yml | Create docker-compose.yml. |
| PASS | Profile Docker compose file exists | docker-compose.profile.yml | Create docker-compose.profile.yml. |
| PASS | Gorz Docker compose file exists | docker-compose.gorz.yml | Create docker-compose.gorz.yml. |
| PASS | No obvious secrets in tracked files | No obvious secret patterns found. | Remove secret material and rotate credentials. |
| WARN | npm audit recommended | package-lock.json exists; audit should run in CI or release prep. | Run npm audit --audit-level=high in CI or before release. |
| WARN | cargo audit recommended | Cargo.lock exists; audit should run in CI or release prep. | Install cargo-audit and run cargo audit before release. |
| WARN | pip-audit recommended | Python project metadata exists; pip-audit is recommended. | Run pip-audit in a pinned environment before release. |
| PASS | Android smoke test source exists | android/gorz/app/src/androidTest/java/com/pirbod/gorz/GorzSmokeTest.kt | Create android/gorz/app/src/androidTest/java/com/pirbod/gorz/GorzSmokeTest.kt. |
| PASS | Android Studio emulator smoke test doc exists | docs/vpn-product/android-studio-emulator-smoke-test.md | Create docs/vpn-product/android-studio-emulator-smoke-test.md. |
| PASS | Android emulator smoke checklist exists | docs/vpn-product/android-emulator-smoke-checklist.md | Create docs/vpn-product/android-emulator-smoke-checklist.md. |
| PASS | android-emulator-smoke Makefile target exists | Found '\nandroid-emulator-smoke:' |  |
| PASS | Compose test tags found | All required tags found. | Add stable Modifier.testTag values for smoke tests. |
| PASS | Android emulator workflow exists | .github/workflows/android-emulator-smoke.yml | Create .github/workflows/android-emulator-smoke.yml. |
| PASS | Managed device config exists | Gradle Managed Device pixel2api30 configured. | Configure Gradle Managed Devices or document emulator runner fallback. |
| WARN | Android emulator tests not configured as PR hard gate | Emulator smoke is intentionally workflow_dispatch/manual-nightly because hosted emulator stability can vary. | Promote emulator smoke to required PR gate after it proves stable. |
| WARN | Production crypto not implemented, documented as gap | Gap phrase 'production crypto' documented. | Document this production gap clearly. |
| WARN | Real tenant auth not implemented, documented as gap | Gap phrase 'tenant' documented. | Document this production gap clearly. |
| PASS | Phase 4 Controlled Release Readiness | Phase 4 checklist evaluated. |  |
| PASS | Phase 4 roadmap closure exists | docs/product/four-phase-roadmap.md | Create docs/product/four-phase-roadmap.md. |
| PASS | SecureValueStore interface exists | android/gorz/app/src/main/java/com/pirbod/gorz/security/SecureValueStore.kt | Create android/gorz/app/src/main/java/com/pirbod/gorz/security/SecureValueStore.kt. |
| PASS | AndroidKeystoreSecureValueStore exists | android/gorz/app/src/main/java/com/pirbod/gorz/security/AndroidKeystoreSecureValueStore.kt | Create android/gorz/app/src/main/java/com/pirbod/gorz/security/AndroidKeystoreSecureValueStore.kt. |
| PASS | RoutePolicyGuard exists | android/gorz/app/src/main/java/com/pirbod/gorz/domain/RoutePolicyGuard.kt | Create android/gorz/app/src/main/java/com/pirbod/gorz/domain/RoutePolicyGuard.kt. |
| PASS | ConfidenceEngine exists | android/gorz/app/src/main/java/com/pirbod/gorz/domain/ConfidenceEngine.kt | Create android/gorz/app/src/main/java/com/pirbod/gorz/domain/ConfidenceEngine.kt. |
| PASS | EvidencePackageV2 exists | android/gorz/app/src/main/java/com/pirbod/gorz/data/model/EvidencePackageV2.kt | Create android/gorz/app/src/main/java/com/pirbod/gorz/data/model/EvidencePackageV2.kt. |
| PASS | SafetyPauseReason exists | android/gorz/app/src/main/java/com/pirbod/gorz/data/model/SafetyPauseReason.kt | Create android/gorz/app/src/main/java/com/pirbod/gorz/data/model/SafetyPauseReason.kt. |
| PASS | Local diagnostics doc exists | docs/vpn-product/local-diagnostics.md | Create docs/vpn-product/local-diagnostics.md. |
| PASS | Phase 4 threat model exists | docs/security/android-phase-4-threat-model.md | Create docs/security/android-phase-4-threat-model.md. |
| PASS | Phase 4 privacy review exists | docs/privacy/android-phase-4-privacy-review.md | Create docs/privacy/android-phase-4-privacy-review.md. |
| PASS | Phase 4 screenshot guide exists | docs/vpn-product/phase-4-screenshot-guide.md | Create docs/vpn-product/phase-4-screenshot-guide.md. |
| PASS | Screenshot capture script exists | scripts/android/capture_phase4_screenshots.py | Create scripts/android/capture_phase4_screenshots.py. |
| PASS | Screenshot report exists | Status: PARTIAL |  |
| PASS | Controlled release process exists | docs/release/phase-4-controlled-release-process.md | Create docs/release/phase-4-controlled-release-process.md. |
| PASS | Controlled release notes exist | docs/release/phase-4-release-notes.md | Create docs/release/phase-4-release-notes.md. |
| PASS | Release candidate manifest script exists | scripts/android/generate_release_candidate_manifest.py | Create scripts/android/generate_release_candidate_manifest.py. |
| PASS | GorzSmokeTest exists | android/gorz/app/src/androidTest/java/com/pirbod/gorz/GorzSmokeTest.kt | Create android/gorz/app/src/androidTest/java/com/pirbod/gorz/GorzSmokeTest.kt. |
| PASS | GorzOfflineConnectSmokeTest exists | android/gorz/app/src/androidTest/java/com/pirbod/gorz/GorzOfflineConnectSmokeTest.kt | Create android/gorz/app/src/androidTest/java/com/pirbod/gorz/GorzOfflineConnectSmokeTest.kt. |
| PASS | Makefile android-emulator-smoke-report target exists | Found '\nandroid-emulator-smoke-report:' |  |
| PASS | Makefile phase4-check target exists | Found '\nphase4-check:' |  |
| PASS | Makefile phase4-screenshots target exists | Found '\nphase4-screenshots:' |  |
| PASS | VERSION is 0.4.0-rc1 | Found '0.4.0-rc1' |  |
| PASS | Android versionName is 0.4.0-rc1 | Found 'versionName = "0.4.0-rc1"' |  |
| PASS | No sensitive Android location permission | Checked for 'ACCESS_FINE_LOCATION' | Remove 'ACCESS_FINE_LOCATION'. |
| PASS | No Android contacts permission | Checked for 'READ_CONTACTS' | Remove 'READ_CONTACTS'. |
| PASS | Android code has no automatic diagnostic upload | Checked phrase 'automatic diagnostic upload' | Remove unsafe phrase 'automatic diagnostic upload'. |
| PASS | Evidence redaction tests exist | android/gorz/app/src/test/java/com/pirbod/gorz/data/repository/EvidenceRepositoryTest.kt | Create android/gorz/app/src/test/java/com/pirbod/gorz/data/repository/EvidenceRepositoryTest.kt. |
| PASS | Route policy tests exist | android/gorz/app/src/test/java/com/pirbod/gorz/domain/RoutePolicyGuardTest.kt | Create android/gorz/app/src/test/java/com/pirbod/gorz/domain/RoutePolicyGuardTest.kt. |
| PASS | Confidence tests exist | android/gorz/app/src/test/java/com/pirbod/gorz/domain/CalculateConfidenceUseCaseTest.kt | Create android/gorz/app/src/test/java/com/pirbod/gorz/domain/CalculateConfidenceUseCaseTest.kt. |
| PASS | Diagnostics tests exist | android/gorz/app/src/test/java/com/pirbod/gorz/data/repository/DiagnosticsRepositoryTest.kt | Create android/gorz/app/src/test/java/com/pirbod/gorz/data/repository/DiagnosticsRepositoryTest.kt. |
| PASS | Safety pause tests exist | android/gorz/app/src/test/java/com/pirbod/gorz/domain/ApplySafetyPauseUseCaseTest.kt | Create android/gorz/app/src/test/java/com/pirbod/gorz/domain/ApplySafetyPauseUseCaseTest.kt. |
| WARN | Production-ready for real use remains NO | The production readiness report package can be READY for review, but the system is not production-ready for real use. | Complete production gaps and independent review before changing production-ready-for-real-use status. |
| PASS | Platform Readiness | Platform engineering and security operations checklist evaluated. |  |
| PASS | Platform: Terraform directory exists | infra/terraform | Create infra/terraform. |
| PASS | Platform: Terraform versions.tf exists | infra/terraform/versions.tf | Create infra/terraform/versions.tf. |
| PASS | Platform: Terraform docs exist | docs/platform/terraform.md | Create docs/platform/terraform.md. |
| PASS | Platform: Kubernetes manifests exist | deploy/kubernetes/kustomization.yaml | Create deploy/kubernetes/kustomization.yaml. |
| PASS | Platform: Kubernetes docs exist | docs/platform/kubernetes.md | Create docs/platform/kubernetes.md. |
| PASS | Platform: NetworkPolicy exists | deploy/kubernetes/networkpolicy.yaml | Create deploy/kubernetes/networkpolicy.yaml. |
| PASS | Platform: Prometheus config exists | observability/prometheus/prometheus.yml | Create observability/prometheus/prometheus.yml. |
| PASS | Platform: Prometheus alert rules exist | observability/prometheus/rules/gozar-safety-alerts.yml | Create observability/prometheus/rules/gozar-safety-alerts.yml. |
| PASS | Platform: Grafana dashboard exists | observability/grafana/dashboards/gozar-controlled-release-dashboard.json | Create observability/grafana/dashboards/gozar-controlled-release-dashboard.json. |
| PASS | Platform: Observability docs exist | docs/platform/observability.md | Create docs/platform/observability.md. |
| PASS | Platform: SIEM rules exist | security/detection/rules/route_policy_violation.yml | Create security/detection/rules/route_policy_violation.yml. |
| PASS | Platform: SIEM sample events exist | security/detection/sample-events/route_policy_violation.json | Create security/detection/sample-events/route_policy_violation.json. |
| PASS | Platform: Detection test script exists | scripts/security/run_detection_tests.py | Create scripts/security/run_detection_tests.py. |
| PASS | Platform: LLM incident summary script exists | ai/incident-summary/incident_summary.py | Create ai/incident-summary/incident_summary.py. |
| PASS | Platform: Deterministic summary output exists | runtime/reports/incident-summary.md | Create runtime/reports/incident-summary.md. |
| PASS | Platform: Detection report exists | runtime/reports/siem-detection-report.md | Create runtime/reports/siem-detection-report.md. |
| SKIPPED | Platform: Terraform check status | runtime/reports/terraform-check-report.json status: SKIPPED |  |
| SKIPPED | Platform: Kubernetes check status | runtime/reports/kubernetes-check-report.json status: SKIPPED |  |
| PASS | Platform: Observability report exists | runtime/reports/observability-check-report.md | Create runtime/reports/observability-check-report.md. |
| PASS | Platform: GitHub Actions terraform workflow exists | .github/workflows/terraform.yml | Create .github/workflows/terraform.yml. |
| PASS | Platform: GitHub Actions kubernetes workflow exists | .github/workflows/kubernetes.yml | Create .github/workflows/kubernetes.yml. |
| PASS | Platform: GitHub Actions detection workflow exists | .github/workflows/detection-and-ai.yml | Create .github/workflows/detection-and-ai.yml. |
| PASS | Platform: GitHub Actions release candidate workflow exists | .github/workflows/release-candidate.yml | Create .github/workflows/release-candidate.yml. |
| PASS | Platform: README has platform sections | All platform sections present. | Update README platform sections. |
| PASS | Platform: Screenshots directory exists | docs/vpn-product/images/phase4 | Create docs/vpn-product/images/phase4. |
| WARN | Platform: Screenshots Android report status | runtime/reports/screenshots/phase4/screenshot-capture-report.json status: PARTIAL |  |
| WARN | Platform: Screenshots platform report status | runtime/reports/screenshots/phase4/platform-screenshot-report.json status: PARTIAL |  |
| PASS | Platform: Demo video script exists | docs/demo/demo-video-script.md | Create docs/demo/demo-video-script.md. |
| WARN | Platform: Demo video exists or pending placeholder exists | Demo video pending placeholder exists. | Record video or add placeholder with recording steps. |
| PASS | Platform: Release candidate manifest exists | runtime/reports/gorz-android-rc-manifest.md | Create runtime/reports/gorz-android-rc-manifest.md. |
| PASS | Platform: Final validation report exists | docs/vpn-product/phase-4-final-validation-report.md | Create docs/vpn-product/phase-4-final-validation-report.md. |
| SKIPPED | Android Gradle build status | Gradle is not installed in this shell; build status is covered by CI workflow when available. | Install Gradle/Android SDK or run Android Studio sync locally. |
| WARN | Known gaps | The platform remains a controlled alpha prototype; production gaps are documented in docs/product/production-gap-analysis.md. | Close release blockers before any real production use. |
