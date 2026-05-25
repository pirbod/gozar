#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = ROOT / "docs" / "demo"
REPORT_DIR = ROOT / "runtime" / "reports"

REQUIRED_FILES = {
    "script": DEMO_DIR / "demo-video-script.md",
    "shotList": DEMO_DIR / "demo-video-shot-list.md",
    "checklist": DEMO_DIR / "demo-video-checklist.md",
    "recordingCommands": DEMO_DIR / "demo-video-recording-commands.md",
    "subtitles": DEMO_DIR / "demo-video-subtitles.srt",
    "demoLink": DEMO_DIR / "demo-video-link.md",
}
VIDEO = DEMO_DIR / "gozar-gorz-phase4-demo.mp4"
PLACEHOLDER = DEMO_DIR / "gozar-gorz-phase4-demo.placeholder.md"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(UTC).isoformat()
    missing = [name for name, path in REQUIRED_FILES.items() if not path.exists()]
    video_status = "PASS" if VIDEO.exists() else "PARTIAL" if PLACEHOLDER.exists() else "FAIL"
    if video_status == "FAIL":
        missing.append("videoOrPlaceholder")
    status = "FAIL" if missing else "PASS" if video_status == "PASS" else "PARTIAL"
    payload = {
        "generatedAt": generated,
        "status": status,
        "videoStatus": video_status,
        "videoPath": str(VIDEO.relative_to(ROOT)) if VIDEO.exists() else "",
        "placeholderPath": str(PLACEHOLDER.relative_to(ROOT)) if PLACEHOLDER.exists() else "",
        "requiredFiles": {name: str(path.relative_to(ROOT)) for name, path in REQUIRED_FILES.items()},
        "missing": missing,
    }
    (REPORT_DIR / "demo-video-check.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (REPORT_DIR / "demo-video-check.md").write_text(render_markdown(payload), encoding="utf-8")
    print(f"Demo video package status: {status}")
    return 0 if status != "FAIL" else 1


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Demo Video Package Check",
        "",
        f"Generated: {payload['generatedAt']}",
        f"Status: {payload['status']}",
        f"Video status: {payload['videoStatus']}",
        f"Video path: `{payload['videoPath'] or 'n/a'}`",
        f"Placeholder path: `{payload['placeholderPath'] or 'n/a'}`",
        "",
        "## Required Files",
        "",
        "| Asset | Path |",
        "| --- | --- |",
    ]
    for name, path in payload["requiredFiles"].items():
        lines.append(f"| {name} | `{path}` |")
    lines.extend(["", "## Missing", ""])
    missing = payload["missing"]
    lines.extend(f"- {name}" for name in missing)
    if not missing:
        lines.append("- none")
    if payload["videoStatus"] == "PARTIAL":
        lines.extend(["", "Demo video pending. Recording plan is complete.", ""])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
