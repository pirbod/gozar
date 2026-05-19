#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "profile_api"))

from profile_api.demo_client import run_lifecycle_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local-only adaptive session profile lifecycle demo.")
    parser.add_argument("--api", default="http://127.0.0.1:8095", help="Profile API base URL.")
    parser.add_argument(
        "--show-demo-payload",
        action="store_true",
        help="Print the decrypted simulated profile payload for local debugging only.",
    )
    args = parser.parse_args()
    run_lifecycle_demo(args.api, show_demo_payload=args.show_demo_payload)


if __name__ == "__main__":
    main()

