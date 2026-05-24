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
    overall = "FAIL" if critical_failures else "PARTIAL" if warnings or skipped else "PASS"

    payload = {
        "title": "Gozar/Gorz Production Readiness Report",
        "generated": generated,
        "summary": {
            "overall": overall,
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
        f"- Critical failures: {summary['critical_failures']}",
        f"- Warnings: {summary['warnings']}",
        f"- Skipped: {summary['skipped']}",
        "",
        "## Checks",
        "",
        "| Status | Check | Detail | Remediation |",
        "| --- | --- | --- | --- |",
    ]
    for check in payload["checks"]:
        lines.append(f"| {check['status']} | {check['name']} | {check['detail']} | {check['remediation']} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
