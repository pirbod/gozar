#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "runtime" / "reports"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    kubectl = shutil.which("kubectl")
    if not kubectl:
        payload = payload_for("SKIPPED", "kubectl is not installed in this shell.", "", [])
        write_reports(payload)
        print("Kubernetes check: SKIPPED")
        return 0
    rendered_path = REPORT_DIR / "gozar-k8s-rendered.yaml"
    kustomize_command = [
        kubectl,
        "kustomize",
        "--load-restrictor=LoadRestrictionsNone",
        "deploy/kubernetes/overlays/local",
    ]
    lint = subprocess.run(kustomize_command, cwd=ROOT, text=True, capture_output=True, check=False)
    if lint.stdout:
        rendered_path.write_text(lint.stdout, encoding="utf-8")
    results = [{"command": "kubectl kustomize --load-restrictor=LoadRestrictionsNone deploy/kubernetes/overlays/local", "exitCode": lint.returncode, "output": tail(lint.stdout + lint.stderr)}]
    status = "PASS" if lint.returncode == 0 else "FAIL"
    if status == "PASS":
        dry = subprocess.run([kubectl, "apply", "--dry-run=client", "--validate=false", "-f", str(rendered_path)], cwd=ROOT, text=True, capture_output=True, check=False)
        results.append({"command": f"kubectl apply --dry-run=client --validate=false -f {rendered_path.relative_to(ROOT)}", "exitCode": dry.returncode, "output": tail(dry.stdout + dry.stderr)})
        status = "PASS" if dry.returncode == 0 else "FAIL"
    payload = payload_for(status, "Kubernetes manifests rendered and dry-run validated." if status == "PASS" else "Kubernetes check failed.", str(rendered_path), results)
    write_reports(payload)
    print(f"Kubernetes check: {status}")
    return 0 if status != "FAIL" else 1


def payload_for(status: str, detail: str, rendered_path: str, results: list[dict[str, object]]) -> dict[str, object]:
    return {"generatedAt": datetime.now(UTC).isoformat(), "status": status, "detail": detail, "renderedPath": rendered_path, "results": results}


def tail(text: str) -> str:
    return "\n".join(text.splitlines()[-80:])


def write_reports(payload: dict[str, object]) -> None:
    (REPORT_DIR / "kubernetes-check-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# Kubernetes Check Report", "", f"Generated: {payload['generatedAt']}", f"Status: {payload['status']}", f"Detail: {payload['detail']}", f"Rendered path: {payload['renderedPath'] or 'n/a'}", ""]
    for result in payload["results"]:
        lines.extend([f"## `{result['command']}`", "", f"Exit code: {result['exitCode']}", "", "```text", str(result["output"]) or "No output.", "```", ""])
    (REPORT_DIR / "kubernetes-check-report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
