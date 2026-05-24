#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TF_DIR = ROOT / "infra" / "terraform"
REPORT_DIR = ROOT / "runtime" / "reports"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    terraform = shutil.which("terraform")
    if not terraform:
        payload = payload_for("SKIPPED", "Terraform is not installed in this shell.", [])
        write_reports(payload)
        print("Terraform check: SKIPPED")
        return 0
    commands = [
        [terraform, "fmt", "-recursive"],
        [terraform, "init", "-backend=false"],
        [terraform, "validate"],
    ]
    results = []
    status = "PASS"
    for command in commands:
        result = subprocess.run(command, cwd=TF_DIR, text=True, capture_output=True, check=False)
        results.append({"command": " ".join(command), "exitCode": result.returncode, "output": tail(result.stdout + result.stderr)})
        if result.returncode != 0:
            status = "FAIL"
            break
    payload = payload_for(status, "Terraform fmt/init/validate completed." if status == "PASS" else "Terraform check failed.", results)
    write_reports(payload)
    print(f"Terraform check: {status}")
    return 0 if status != "FAIL" else 1


def payload_for(status: str, detail: str, results: list[dict[str, object]]) -> dict[str, object]:
    return {"generatedAt": datetime.now(UTC).isoformat(), "status": status, "detail": detail, "results": results}


def tail(text: str) -> str:
    return "\n".join(text.splitlines()[-80:])


def write_reports(payload: dict[str, object]) -> None:
    (REPORT_DIR / "terraform-check-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# Terraform Check Report", "", f"Generated: {payload['generatedAt']}", f"Status: {payload['status']}", f"Detail: {payload['detail']}", ""]
    for result in payload["results"]:
        lines.extend([f"## `{result['command']}`", "", f"Exit code: {result['exitCode']}", "", "```text", str(result["output"]) or "No output.", "```", ""])
    (REPORT_DIR / "terraform-check-report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
