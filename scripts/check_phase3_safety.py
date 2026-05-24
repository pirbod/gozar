#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID_DIR = ROOT / "android" / "gorz"

RISKY_REGEXES = {
    "device-wide IPv4 route": re.compile(r"addRoute\s*\(\s*\"0\.0\.0\.0\""),
    "device-wide IPv6 route": re.compile(r"addRoute\s*\(\s*\"::\""),
    "public relay " + "discovery": re.compile(r"public\s+relay\s+discovery", re.IGNORECASE),
    "public gateway discovery": re.compile(r"public\s+gateway\s+discovery", re.IGNORECASE),
    "bridge discovery": re.compile(r"bridge\s+discovery", re.IGNORECASE),
    "external probing": re.compile(r"external\s+probing", re.IGNORECASE),
    "socket forwarding": re.compile(r"socket\s+forwarding", re.IGNORECASE),
    "automatic diagnostic upload": re.compile(r"automatic\s+diagnostic\s+upload", re.IGNORECASE),
    "phone number access": re.compile(r"READ_PHONE_NUMBERS|READ_PHONE_STATE|phone\s+number\s+access", re.IGNORECASE),
    "contacts permission": re.compile(r"READ_CONTACTS|WRITE_CONTACTS|GET_ACCOUNTS|contacts\s+permission", re.IGNORECASE),
    "fine location permission": re.compile(r"ACCESS_FINE_LOCATION|fine\s+location\s+permission", re.IGNORECASE),
    "coarse location permission": re.compile(r"ACCESS_COARSE_LOCATION|coarse\s+location\s+permission", re.IGNORECASE),
}

SCAN_SUFFIXES = {".kt", ".kts", ".xml", ".md", ".properties"}


def main() -> None:
    violations: list[str] = []
    for path in sorted(ANDROID_DIR.rglob("*")):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in RISKY_REGEXES.items():
                if pattern.search(line):
                    violations.append(f"{path.relative_to(ROOT)}:{line_number}: unsafe Phase 3 pattern: {label}")

    if violations:
        raise SystemExit("\n".join(violations))
    print("Phase 3 Android safety guard passed.")


if __name__ == "__main__":
    main()
