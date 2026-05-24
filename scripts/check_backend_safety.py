#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = ROOT / "python"
SCAN_SUFFIXES = {".py", ".md"}

BLOCKED = {
    "public relay " + "discovery": re.compile(r"public\s+relay\s+discovery", re.IGNORECASE),
    "public gateway " + "discovery": re.compile(r"public\s+gateway\s+discovery", re.IGNORECASE),
    "bridge discovery": re.compile(r"bridge\s+discovery", re.IGNORECASE),
    "public probing": re.compile(r"public\s+probing", re.IGNORECASE),
    "external probing": re.compile(r"external\s+probing", re.IGNORECASE),
    "automatic diagnostic upload": re.compile(r"automatic\s+diagnostic\s+upload", re.IGNORECASE),
    "collect phone number": re.compile(r"collect\s+phone\s+number", re.IGNORECASE),
    "collect contacts": re.compile(r"collect\s+contacts", re.IGNORECASE),
    "collect exact location": re.compile(r"collect\s+exact\s+location", re.IGNORECASE),
    "collect public IP history": re.compile(r"collect\s+public\s+IP\s+history", re.IGNORECASE),
}

ALLOW_HINTS = (
    "no ",
    "not ",
    "disabled",
    "blocked",
    "simulated diagnostics",
    "local-only",
    "local only",
)


def main() -> None:
    violations: list[str] = []
    for path in sorted(PYTHON_DIR.rglob("*")):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            lowered = line.lower()
            for label, pattern in BLOCKED.items():
                if pattern.search(line) and not any(hint in lowered for hint in ALLOW_HINTS):
                    violations.append(f"{path.relative_to(ROOT)}:{line_number}: unsafe backend phrase: {label}")

    print("Backend safety check")
    if violations:
        print("FAIL")
        print("\n".join(violations))
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
