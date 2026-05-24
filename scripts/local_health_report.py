#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.request
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "runtime" / "reports"


@dataclass(frozen=True)
class HealthItem:
    name: str
    status: str
    detail: str


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a local-only Gozar/Gorz health report.")
    parser.add_argument("--with-local-endpoints", action="store_true", help="Check localhost health endpoints.")
    args = parser.parse_args()

    items = [
        _exists("docker-compose.yml", ROOT / "docker-compose.yml"),
        _exists("docker-compose.gorz.yml", ROOT / "docker-compose.gorz.yml"),
        _exists("docker-compose.profile.yml", ROOT / "docker-compose.profile.yml"),
        _exists("runtime folder", ROOT / "runtime"),
        _exists("profile runtime folder", ROOT / "runtime" / "profile"),
        _exists("gorz runtime folder", ROOT / "runtime" / "gorz"),
        _exists("control-plane audit log", ROOT / "runtime" / "control-plane" / "audit.log.ndjson"),
    ]

    if args.with_local_endpoints:
        items.append(_endpoint("Profile API", "http://127.0.0.1:8095/api/profile/health"))
        items.append(_endpoint("Gorz API", "http://127.0.0.1:8090/api/gorz/health"))
    else:
        items.append(HealthItem("local endpoints", "SKIPPED", "Pass --with-local-endpoints to check localhost APIs."))

    generated = datetime.now(UTC).isoformat()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"generated": generated, "items": [asdict(item) for item in items]}
    (REPORT_DIR / "local-health-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (REPORT_DIR / "local-health-report.md").write_text(_markdown(generated, items), encoding="utf-8")
    print(f"Wrote {REPORT_DIR.relative_to(ROOT)}/local-health-report.md")


def _exists(name: str, path: Path) -> HealthItem:
    return HealthItem(name, "PASS" if path.exists() else "WARN", str(path.relative_to(ROOT)))


def _endpoint(name: str, url: str) -> HealthItem:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return HealthItem(name, "PASS" if response.status < 400 else "WARN", f"{url} returned {response.status}")
    except Exception as exc:
        return HealthItem(name, "WARN", f"{url} unavailable: {exc}")


def _markdown(generated: str, items: list[HealthItem]) -> str:
    lines = ["# Local Health Report", "", f"Generated: {generated}", "", "| Status | Check | Detail |", "| --- | --- | --- |"]
    lines.extend(f"| {item.status} | {item.name} | {item.detail} |" for item in items)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
