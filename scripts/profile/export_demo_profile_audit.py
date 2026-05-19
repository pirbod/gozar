#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "runtime" / "profile" / "latest-audit.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the redacted local profile audit bundle.")
    parser.add_argument("--api", default="http://127.0.0.1:8095", help="Profile API base URL.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output JSON file path.")
    args = parser.parse_args()

    with httpx.Client(base_url=args.api, timeout=10.0) as client:
        response = client.get("/api/profile/audit/export")
        response.raise_for_status()
        bundle = response.json()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    print(f"saved redacted audit bundle: {output}")
    print(json.dumps(bundle["redaction"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

