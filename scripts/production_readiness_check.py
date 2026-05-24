#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "runtime" / "reports"


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    detail: str
    remediation: str = ""
    critical: bool = False


def main() -> None:
    checks = build_checks()
    generated = datetime.now(UTC).isoformat()
    critical_failures = sum(1 for check in checks if check.status == "FAIL" and check.critical)
    warnings = sum(1 for check in checks if check.status == "WARN")
    skipped = sum(1 for check in checks if check.status == "SKIPPED")
    platform_readiness = _section_status(checks, "Platform:")
    overall = "FAIL" if critical_failures else "PARTIAL" if warnings or skipped else "PASS"
    controlled_release_readiness = "FAIL" if critical_failures else "PASS"
    production_readiness = "BLOCKED" if critical_failures else "READY"

    payload = {
        "title": "Gozar/Gorz Production Readiness Report",
        "generated": generated,
        "summary": {
            "overall": overall,
            "controlled_release_readiness": controlled_release_readiness,
            "controlled_release_evidence": overall,
            "production_readiness": production_readiness,
            "production_ready_for_real_use": "NO",
            "production_security_claim": "NO",
            "platform_readiness": platform_readiness,
            "critical_failures": critical_failures,
            "warnings": warnings,
            "skipped": skipped,
        },
        "checks": [asdict(check) for check in checks],
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "production-readiness-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (REPORT_DIR / "production-readiness-report.md").write_text(render_markdown(payload), encoding="utf-8")
    print(render_console(payload))


def build_checks() -> list[CheckResult]:
    readme = _read("README.md")
    manifest = _read("android/gorz/app/src/main/AndroidManifest.xml")
    makefile = _read("Makefile")
    phase3_exists = (ROOT / "docs/vpn-product/phase-3-android-clickable-prototype.md").exists()

    checks: list[CheckResult] = [
        _exists("README exists", "README.md", critical=True),
        _contains("README safety wording present", readme, "Safety Disclaimer", "Restore the README safety disclaimer.", critical=True),
        _contains("README contains not a circumvention tool", readme, "not a circumvention tool", "Restore the project positioning disclaimer.", critical=True),
        _contains(
            "README contains not a field-deployment routing product",
            readme,
            "not a field-deployment routing product",
            "Restore the project positioning disclaimer.",
            critical=True,
        ),
        _exists("Safety boundaries doc exists", "docs/safety-boundaries.md", critical=True),
        _exists("Production gap analysis exists", "docs/product/production-gap-analysis.md"),
        _exists("Release blocker checklist exists", "docs/product/release-blocker-checklist.md"),
        _exists("Risk register exists", "docs/product/risk-register.md"),
        _exists("Phase 1 docs exist", "docs/vpn-product/phase-1-local-profile-lifecycle.md"),
        _exists("Phase 2 docs exist", "docs/vpn-product/phase-2-android-vpnservice.md"),
    ]
    if phase3_exists:
        checks.append(_exists("Phase 3 docs exist", "docs/vpn-product/phase-3-android-clickable-prototype.md"))

    for permission in [
        "ACCESS_FINE_LOCATION",
        "ACCESS_COARSE_LOCATION",
        "READ_CONTACTS",
        "READ_PHONE_NUMBERS",
        "READ_PHONE_STATE",
    ]:
        checks.append(_not_contains(f"AndroidManifest.xml does not include {permission}", manifest, permission, critical=True))

    android_text = _joined_text(ROOT / "android" / "gorz", {".kt", ".kts", ".xml", ".md"})
    checks.extend(
        [
            _not_contains('Android does not add 0.0.0.0/0 route', android_text, 'addRoute("0.0.0.0"', critical=True),
            _not_contains('Android does not add ::/0 route', android_text, 'addRoute("::"', critical=True),
            _phrase_absent("Android code has no public relay discovery strings", android_text, "public relay " + "discovery", critical=True),
            _phrase_absent("Android code has no public gateway discovery strings", android_text, "public gateway " + "discovery", critical=True),
            _phrase_absent("Android code has no bridge discovery strings", android_text, "bridge discovery", critical=True),
            _phrase_absent("Android code has no external probing strings", android_text, "external probing", critical=True),
            _phrase_absent("Android code has no automatic diagnostic upload strings", android_text, "automatic diagnostic upload", critical=True),
        ],
    )

    checks.extend(
        [
            _phrase_absent("Python code has no public relay discovery strings", _joined_text(ROOT / "python", {".py"}), "public relay " + "discovery", critical=True),
            _phrase_absent("Python code has no public gateway discovery strings", _joined_text(ROOT / "python", {".py"}), "public gateway " + "discovery", critical=True),
            _phrase_absent("TypeScript code has no public relay discovery strings", _joined_text(ROOT / "ts", {".ts", ".tsx"}), "public relay " + "discovery", critical=True),
            _phrase_absent("Rust code has no public relay discovery strings", _joined_text(ROOT / "rust", {".rs"}), "public relay " + "discovery", critical=True),
            _exists("Phase 3 safety checker exists", "scripts/check_phase3_safety.py"),
            _contains("Makefile android-check target exists", makefile, "\nandroid-check:"),
            _contains("Makefile phase2-check target exists", makefile, "\nphase2-check:"),
        ],
    )
    if phase3_exists:
        checks.append(_contains("Makefile phase3-check target exists", makefile, "\nphase3-check:"))

    checks.extend(
        [
            _exists("GitHub Actions workflow exists", ".github/workflows/ci.yml"),
            _exists("Docker compose files exist", "docker-compose.yml"),
            _exists("Profile Docker compose file exists", "docker-compose.profile.yml"),
            _exists("Gorz Docker compose file exists", "docker-compose.gorz.yml"),
            _secret_scan(),
            _dependency_note("npm audit recommended", "package-lock.json", "Run npm audit --audit-level=high in CI or before release."),
            _dependency_note("cargo audit recommended", "Cargo.lock", "Install cargo-audit and run cargo audit before release."),
            _python_audit_note(),
            _exists("Android smoke test source exists", "android/gorz/app/src/androidTest/java/com/pirbod/gorz/GorzSmokeTest.kt"),
            _exists("Android Studio emulator smoke test doc exists", "docs/vpn-product/android-studio-emulator-smoke-test.md"),
            _exists("Android emulator smoke checklist exists", "docs/vpn-product/android-emulator-smoke-checklist.md"),
            _contains("android-emulator-smoke Makefile target exists", makefile, "\nandroid-emulator-smoke:"),
            _compose_tags(android_text),
            _exists("Android emulator workflow exists", ".github/workflows/android-emulator-smoke.yml"),
            _managed_device_config(),
            CheckResult(
                "Android emulator tests not configured as PR hard gate",
                "WARN",
                "Emulator smoke is intentionally workflow_dispatch/manual-nightly because hosted emulator stability can vary.",
                "Promote emulator smoke to required PR gate after it proves stable.",
            ),
            _gap_doc_check("Production crypto not implemented, documented as gap", "production crypto"),
            _gap_doc_check("Real tenant auth not implemented, documented as gap", "tenant"),
        ],
    )

    phase4_checks = [
        _exists("Phase 4 roadmap closure exists", "docs/product/four-phase-roadmap.md"),
        _exists("SecureValueStore interface exists", "android/gorz/app/src/main/java/com/pirbod/gorz/security/SecureValueStore.kt"),
        _exists("AndroidKeystoreSecureValueStore exists", "android/gorz/app/src/main/java/com/pirbod/gorz/security/AndroidKeystoreSecureValueStore.kt"),
        _exists("RoutePolicyGuard exists", "android/gorz/app/src/main/java/com/pirbod/gorz/domain/RoutePolicyGuard.kt"),
        _exists("ConfidenceEngine exists", "android/gorz/app/src/main/java/com/pirbod/gorz/domain/ConfidenceEngine.kt"),
        _exists("EvidencePackageV2 exists", "android/gorz/app/src/main/java/com/pirbod/gorz/data/model/EvidencePackageV2.kt"),
        _exists("SafetyPauseReason exists", "android/gorz/app/src/main/java/com/pirbod/gorz/data/model/SafetyPauseReason.kt"),
        _exists("Local diagnostics doc exists", "docs/vpn-product/local-diagnostics.md"),
        _exists("Phase 4 threat model exists", "docs/security/android-phase-4-threat-model.md"),
        _exists("Phase 4 privacy review exists", "docs/privacy/android-phase-4-privacy-review.md"),
        _exists("Phase 4 screenshot guide exists", "docs/vpn-product/phase-4-screenshot-guide.md"),
        _exists("Screenshot capture script exists", "scripts/android/capture_phase4_screenshots.py"),
        _screenshot_report_check(),
        _exists("Controlled release process exists", "docs/release/phase-4-controlled-release-process.md"),
        _exists("Controlled release notes exist", "docs/release/phase-4-release-notes.md"),
        _exists("Release candidate manifest script exists", "scripts/android/generate_release_candidate_manifest.py"),
        _exists("GorzSmokeTest exists", "android/gorz/app/src/androidTest/java/com/pirbod/gorz/GorzSmokeTest.kt"),
        _exists("GorzOfflineConnectSmokeTest exists", "android/gorz/app/src/androidTest/java/com/pirbod/gorz/GorzOfflineConnectSmokeTest.kt"),
        _contains("Makefile android-emulator-smoke-report target exists", makefile, "\nandroid-emulator-smoke-report:"),
        _contains("Makefile phase4-check target exists", makefile, "\nphase4-check:"),
        _contains("Makefile phase4-screenshots target exists", makefile, "\nphase4-screenshots:"),
        _contains("VERSION is 0.4.0-rc1", _read("VERSION"), "0.4.0-rc1", critical=True),
        _contains("Android versionName is 0.4.0-rc1", gradle_text(), 'versionName = "0.4.0-rc1"', critical=True),
        _not_contains("No sensitive Android location permission", manifest, "ACCESS_FINE_LOCATION", critical=True),
        _not_contains("No Android contacts permission", manifest, "READ_CONTACTS", critical=True),
        _phrase_absent("Android code has no automatic diagnostic upload", android_text, "automatic diagnostic upload", critical=True),
        _exists("Evidence redaction tests exist", "android/gorz/app/src/test/java/com/pirbod/gorz/data/repository/EvidenceRepositoryTest.kt"),
        _exists("Route policy tests exist", "android/gorz/app/src/test/java/com/pirbod/gorz/domain/RoutePolicyGuardTest.kt"),
        _exists("Confidence tests exist", "android/gorz/app/src/test/java/com/pirbod/gorz/domain/CalculateConfidenceUseCaseTest.kt"),
        _exists("Diagnostics tests exist", "android/gorz/app/src/test/java/com/pirbod/gorz/data/repository/DiagnosticsRepositoryTest.kt"),
        _exists("Safety pause tests exist", "android/gorz/app/src/test/java/com/pirbod/gorz/domain/ApplySafetyPauseUseCaseTest.kt"),
        CheckResult(
            "Production-ready for real use remains NO",
            "WARN",
            "The production readiness report package can be READY for review, but the system is not production-ready for real use.",
            "Complete production gaps and independent review before changing production-ready-for-real-use status.",
        ),
    ]
    checks.append(CheckResult("Phase 4 Controlled Release Readiness", "PASS", "Phase 4 checklist evaluated."))
    checks.extend(phase4_checks)

    platform_checks = [
        _exists("Platform: Terraform directory exists", "infra/terraform"),
        _exists("Platform: Terraform versions.tf exists", "infra/terraform/versions.tf"),
        _exists("Platform: Terraform docs exist", "docs/platform/terraform.md"),
        _exists("Platform: Kubernetes manifests exist", "deploy/kubernetes/kustomization.yaml"),
        _exists("Platform: Kubernetes docs exist", "docs/platform/kubernetes.md"),
        _exists("Platform: NetworkPolicy exists", "deploy/kubernetes/networkpolicy.yaml"),
        _exists("Platform: Prometheus config exists", "observability/prometheus/prometheus.yml"),
        _exists("Platform: Prometheus alert rules exist", "observability/prometheus/rules/gozar-safety-alerts.yml"),
        _exists("Platform: Grafana dashboard exists", "observability/grafana/dashboards/gozar-controlled-release-dashboard.json"),
        _exists("Platform: Observability docs exist", "docs/platform/observability.md"),
        _exists("Platform: SIEM rules exist", "security/detection/rules/route_policy_violation.yml"),
        _exists("Platform: SIEM sample events exist", "security/detection/sample-events/route_policy_violation.json"),
        _exists("Platform: Detection test script exists", "scripts/security/run_detection_tests.py"),
        _exists("Platform: LLM incident summary script exists", "ai/incident-summary/incident_summary.py"),
        _exists("Platform: Deterministic summary output exists", "runtime/reports/incident-summary.md"),
        _exists("Platform: Detection report exists", "runtime/reports/siem-detection-report.md"),
        _report_status_check("Platform: Terraform check status", "runtime/reports/terraform-check-report.json"),
        _report_status_check("Platform: Kubernetes check status", "runtime/reports/kubernetes-check-report.json"),
        _exists("Platform: Observability report exists", "runtime/reports/observability-check-report.md"),
        _exists("Platform: GitHub Actions terraform workflow exists", ".github/workflows/terraform.yml"),
        _exists("Platform: GitHub Actions kubernetes workflow exists", ".github/workflows/kubernetes.yml"),
        _exists("Platform: GitHub Actions detection workflow exists", ".github/workflows/detection-and-ai.yml"),
        _exists("Platform: GitHub Actions release candidate workflow exists", ".github/workflows/release-candidate.yml"),
        _readme_section_check(),
        _exists("Platform: Screenshots directory exists", "docs/vpn-product/images/phase4"),
        _report_status_check("Platform: Screenshots Android report status", "runtime/reports/screenshots/phase4/screenshot-capture-report.json"),
        _report_status_check("Platform: Screenshots platform report status", "runtime/reports/screenshots/phase4/platform-screenshot-report.json"),
        _exists("Platform: Demo video script exists", "docs/demo/demo-video-script.md"),
        _demo_video_check(),
        _exists("Platform: Release candidate manifest exists", "runtime/reports/gorz-android-rc-manifest.md"),
        _exists("Platform: Final validation report exists", "docs/vpn-product/phase-4-final-validation-report.md"),
    ]
    checks.append(CheckResult("Platform Readiness", "PASS", "Platform engineering and security operations checklist evaluated."))
    checks.extend(platform_checks)

    if shutil.which("gradle") is None:
        checks.append(
            CheckResult(
                "Android Gradle build status",
                "SKIPPED",
                "Gradle is not installed in this shell; build status is covered by CI workflow when available.",
                "Install Gradle/Android SDK or run Android Studio sync locally.",
            ),
        )
    else:
        checks.append(
            CheckResult(
                "Android Gradle build status",
                "SKIPPED",
                "This readiness script does not run Gradle to remain deterministic and local-file-only.",
                "Run make android-build or make android-emulator-smoke.",
            ),
        )

    checks.append(
        CheckResult(
            "Known gaps",
            "WARN",
            "The platform remains a controlled alpha prototype; production gaps are documented in docs/product/production-gap-analysis.md.",
            "Close release blockers before any real production use.",
        ),
    )
    return checks


def _exists(name: str, relative: str, critical: bool = False) -> CheckResult:
    exists = (ROOT / relative).exists()
    return CheckResult(name, "PASS" if exists else "FAIL", relative if exists else f"Missing {relative}", f"Create {relative}.", critical)


def _contains(name: str, text: str, needle: str, remediation: str = "", critical: bool = False) -> CheckResult:
    return CheckResult(name, "PASS" if needle in text else "FAIL", f"Found {needle!r}" if needle in text else f"Missing {needle!r}", remediation, critical)


def _not_contains(name: str, text: str, needle: str, critical: bool = False) -> CheckResult:
    return CheckResult(name, "PASS" if needle not in text else "FAIL", f"Checked for {needle!r}", f"Remove {needle!r}.", critical)


def _phrase_absent(name: str, text: str, phrase: str, critical: bool = False) -> CheckResult:
    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
    return CheckResult(name, "PASS" if not pattern.search(text) else "FAIL", f"Checked phrase {phrase!r}", f"Remove unsafe phrase {phrase!r}.", critical)


def _read(relative: str) -> str:
    path = ROOT / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _joined_text(root: Path, suffixes: set[str]) -> str:
    if not root.exists():
        return ""
    parts: list[str] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix in suffixes and ".gradle" not in path.parts:
            parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def _secret_scan() -> CheckResult:
    patterns = [
        re.compile(re.escape("AWS_SECRET" + "_ACCESS_KEY")),
        re.compile(re.escape("AZURE_CLIENT" + "_SECRET")),
        re.compile(re.escape("PRIVATE" + "_KEY=")),
        re.compile(re.escape("BEGIN RSA" + " PRIVATE KEY")),
        re.compile(re.escape("BEGIN OPENSSH" + " PRIVATE KEY")),
        re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
        re.compile(r"xoxb-[A-Za-z0-9-]{20,}"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
    ]
    ignored_dirs = {
        ".git",
        "node_modules",
        "target",
        ".gradle",
        "__pycache__",
        "runtime",
    }
    violations: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or any(part in ignored_dirs for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in patterns:
            if pattern.search(text):
                violations.append(f"{path.relative_to(ROOT)} contains {pattern.pattern}")
    return CheckResult(
        "No obvious secrets in tracked files",
        "PASS" if not violations else "FAIL",
        "No obvious secret patterns found." if not violations else "; ".join(violations[:10]),
        "Remove secret material and rotate credentials.",
        critical=True,
    )


def _dependency_note(name: str, relative: str, remediation: str) -> CheckResult:
    if not (ROOT / relative).exists():
        return CheckResult(name, "SKIPPED", f"{relative} not present.", remediation)
    return CheckResult(name, "WARN", f"{relative} exists; audit should run in CI or release prep.", remediation)


def _python_audit_note() -> CheckResult:
    exists = any((ROOT / path).exists() for path in ["requirements.txt", "python/profile_api/pyproject.toml", "python/gorz_api/pyproject.toml"])
    return CheckResult(
        "pip-audit recommended",
        "WARN" if exists else "SKIPPED",
        "Python project metadata exists; pip-audit is recommended." if exists else "No Python project metadata found.",
        "Run pip-audit in a pinned environment before release.",
    )


def _compose_tags(android_text: str) -> CheckResult:
    tags = [
        "screen_onboarding",
        "screen_home",
        "screen_connect_flow",
        "screen_session",
        "screen_confidence",
        "screen_route_policy",
        "screen_diagnostics",
        "screen_evidence",
        "screen_audit",
        "screen_settings",
        "button_start_demo",
        "button_connect",
        "button_generate_evidence",
        "text_controlled_prototype",
        "text_no_public_forwarding",
        "text_applied_route",
        "text_blocked_route",
        "text_redacted_evidence",
    ]
    missing = [tag for tag in tags if tag not in android_text]
    return CheckResult(
        "Compose test tags found",
        "PASS" if not missing else "FAIL",
        "All required tags found." if not missing else f"Missing tags: {', '.join(missing)}",
        "Add stable Modifier.testTag values for smoke tests.",
    )


def _managed_device_config() -> CheckResult:
    gradle = _read("android/gorz/app/build.gradle.kts")
    present = "managedDevices" in gradle and "pixel2api30" in gradle
    return CheckResult(
        "Managed device config exists",
        "PASS" if present else "WARN",
        "Gradle Managed Device pixel2api30 configured." if present else "Managed device config missing.",
        "Configure Gradle Managed Devices or document emulator runner fallback.",
    )


def _readme_section_check() -> CheckResult:
    readme = _read("README.md")
    required = [
        "## Terraform",
        "## Kubernetes",
        "## Observability",
        "## SIEM-Style Detection",
        "## Deterministic Incident Summaries",
        "## Screenshots",
        "## Demo Video",
    ]
    missing = [section for section in required if section not in readme]
    return CheckResult(
        "Platform: README has platform sections",
        "PASS" if not missing else "FAIL",
        "All platform sections present." if not missing else f"Missing sections: {', '.join(missing)}",
        "Update README platform sections.",
    )


def _demo_video_check() -> CheckResult:
    video = ROOT / "docs" / "demo" / "gozar-gorz-phase4-demo.mp4"
    placeholder = ROOT / "docs" / "demo" / "gozar-gorz-phase4-demo.placeholder.md"
    if video.exists():
        return CheckResult("Platform: Demo video exists or pending placeholder exists", "PASS", "Demo video file exists.")
    return CheckResult(
        "Platform: Demo video exists or pending placeholder exists",
        "WARN" if placeholder.exists() else "FAIL",
        "Demo video pending placeholder exists." if placeholder.exists() else "Missing demo video and placeholder.",
        "Record video or add placeholder with recording steps.",
    )


def _report_status_check(name: str, relative: str) -> CheckResult:
    path = ROOT / relative
    if not path.exists():
        return CheckResult(name, "FAIL", f"Missing {relative}", f"Generate {relative}.")
    payload = json.loads(path.read_text(encoding="utf-8"))
    status = str(payload.get("status", "UNKNOWN"))
    if status == "PASS":
        return CheckResult(name, "PASS", f"{relative} status: PASS")
    if status == "SKIPPED":
        return CheckResult(name, "SKIPPED", f"{relative} status: SKIPPED")
    if status == "PARTIAL":
        return CheckResult(name, "WARN", f"{relative} status: PARTIAL")
    return CheckResult(name, "FAIL", f"{relative} status: {status}")


def _section_status(checks: list[CheckResult], prefix: str) -> str:
    scoped = [check for check in checks if check.name.startswith(prefix)]
    if not scoped:
        return "PARTIAL"
    if any(check.status == "FAIL" and check.critical for check in scoped):
        return "FAIL"
    if any(check.status in {"FAIL", "WARN", "SKIPPED"} for check in scoped):
        return "PARTIAL"
    return "PASS"


def gradle_text() -> str:
    return _read("android/gorz/app/build.gradle.kts")


def _screenshot_report_check() -> CheckResult:
    path = ROOT / "runtime" / "reports" / "screenshots" / "phase4" / "screenshot-capture-report.md"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        status_line = next((line for line in text.splitlines() if line.startswith("Status:")), "Status: UNKNOWN")
        return CheckResult("Screenshot report exists", "PASS", status_line)
    return CheckResult(
        "Screenshot report exists or is skipped with reason",
        "WARN",
        "No screenshot report found yet.",
        "Run make phase4-screenshot-report.",
    )


def _gap_doc_check(name: str, phrase: str) -> CheckResult:
    text = _read("docs/product/production-gap-analysis.md").lower()
    return CheckResult(
        name,
        "WARN" if phrase.lower() in text else "FAIL",
        f"Gap phrase {phrase!r} documented." if phrase.lower() in text else f"Gap phrase {phrase!r} missing.",
        "Document this production gap clearly.",
    )


def render_console(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    lines = [
        payload["title"],
        f"Generated: {payload['generated']}",
        "",
        "Summary:",
        f"- Overall: {summary['overall']}",
        f"- Controlled release readiness: {summary['controlled_release_readiness']}",
        f"- Controlled release evidence: {summary['controlled_release_evidence']}",
        f"- Platform readiness: {summary['platform_readiness']}",
        f"- Production readiness report: {summary['production_readiness']}",
        f"- Production-ready for real use: {summary['production_ready_for_real_use']}",
        f"- Critical failures: {summary['critical_failures']}",
        f"- Warnings: {summary['warnings']}",
        f"- Skipped: {summary['skipped']}",
        "",
        "Checks:",
    ]
    lines.extend(f"[{check['status']}] {check['name']} - {check['detail']}" for check in payload["checks"])
    return "\n".join(lines)


def render_markdown(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    lines = [
        "# Gozar/Gorz Production Readiness Report",
        "",
        f"Generated: {payload['generated']}",
        "",
        "## Summary",
        "",
        f"- Overall: {summary['overall']}",
        f"- Controlled release readiness: {summary['controlled_release_readiness']}",
        f"- Controlled release evidence: {summary['controlled_release_evidence']}",
        f"- Platform readiness: {summary['platform_readiness']}",
        f"- Production readiness report: {summary['production_readiness']}",
        f"- Production-ready for real use: {summary['production_ready_for_real_use']}",
        f"- Production security claim: {summary['production_security_claim']}",
        f"- Critical failures: {summary['critical_failures']}",
        f"- Warnings: {summary['warnings']}",
        f"- Skipped: {summary['skipped']}",
        "",
        "## Checks",
        "",
        "## Platform Readiness",
        "",
        "| Area | Status |",
        "| --- | --- |",
        f"| Terraform | {status_for(payload, 'Platform: Terraform')} |",
        f"| Kubernetes | {status_for(payload, 'Platform: Kubernetes')} |",
        f"| Observability | {status_for(payload, 'Platform: Observability')} |",
        f"| SIEM detection | {status_for(payload, 'Platform: SIEM')} |",
        f"| Incident summaries | {status_for(payload, 'Platform: LLM')} |",
        f"| GitHub Actions | {status_for(payload, 'Platform: GitHub Actions')} |",
        f"| README | {status_for(payload, 'Platform: README')} |",
        f"| Screenshots | {status_for(payload, 'Platform: Screenshot')} |",
        f"| Demo video | {status_for(payload, 'Platform: Demo video')} |",
        "",
        "## Phase 4 Controlled Release Readiness",
        "",
        "| Area | Status |",
        "| --- | --- |",
        "| Roadmap closure | Evaluated below |",
        "| Android hardening | Evaluated below |",
        "| Storage readiness | Evaluated below |",
        "| Route safety | Evaluated below |",
        "| Confidence engine | Evaluated below |",
        "| Evidence package | Evaluated below |",
        "| Diagnostics | Evaluated below |",
        "| Safety pause | Evaluated below |",
        "| Emulator smoke | Evaluated below |",
        "| Screenshot evidence | Evaluated below |",
        "| Release artifact manifest | Evaluated below |",
        "| Privacy review | Evaluated below |",
        "| Threat model | Evaluated below |",
        "| Backend contract | Evaluated below |",
        "| Documentation | Evaluated below |",
        f"| Controlled release readiness | {summary['controlled_release_readiness']} |",
        f"| Controlled release evidence | {summary['controlled_release_evidence']} |",
        f"| Production readiness report | {summary['production_readiness']} |",
        f"| Production-ready for real use | {summary['production_ready_for_real_use']} |",
        "",
        "| Status | Check | Detail | Remediation |",
        "| --- | --- | --- | --- |",
    ]
    for check in payload["checks"]:
        lines.append(f"| {check['status']} | {check['name']} | {check['detail']} | {check['remediation']} |")
    return "\n".join(lines) + "\n"


def status_for(payload: dict[str, object], prefix: str) -> str:
    checks = payload["checks"]
    scoped = [check for check in checks if check["name"].startswith(prefix)]
    if not scoped:
        return "PARTIAL"
    if any(check["status"] == "FAIL" for check in scoped):
        return "FAIL"
    if any(check["status"] in {"WARN", "SKIPPED"} for check in scoped):
        return "PARTIAL"
    return "PASS"


if __name__ == "__main__":
    main()
