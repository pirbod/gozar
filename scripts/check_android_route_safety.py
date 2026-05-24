#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID_DIR = ROOT / "android" / "gorz"
SCAN_SUFFIXES = {".kt", ".kts", ".xml", ".md"}

BLOCKED_PATTERNS = {
    "unsafe addRoute IPv4": re.compile(r"addRoute\s*\(\s*\"0\.0\.0\.0\"(?:\s*,\s*0)?"),
    "unsafe addRoute IPv6": re.compile(r"addRoute\s*\(\s*\"::\"(?:\s*,\s*0)?"),
}

TEXTUAL_BLOCKED_ROUTES = ("0.0.0.0/0", "::/0")
TEXTUAL_ALLOW_HINTS = (
    "blocked",
    "Blocked",
    "reject",
    "Reject",
    "unsafe route",
    "BlockedUnsafeRoute",
    "isBlockedRouteExplicit",
    "assertFalse",
    "does not contain",
)


def main() -> None:
    violations: list[str] = []
    for path in sorted(ANDROID_DIR.rglob("*")):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in BLOCKED_PATTERNS.items():
                if pattern.search(line):
                    violations.append(_format(path, line_number, label))
            if "src/test" not in path.as_posix() and "src/androidTest" not in path.as_posix():
                for route in TEXTUAL_BLOCKED_ROUTES:
                    if route in line and not any(hint in line for hint in TEXTUAL_ALLOW_HINTS):
                        violations.append(_format(path, line_number, f"unqualified device-wide route literal {route}"))

    print("Android route safety check")
    if violations:
        print("FAIL")
        print("\n".join(violations))
        raise SystemExit(1)
    print("PASS")


def _format(path: Path, line_number: int, label: str) -> str:
    return f"{path.relative_to(ROOT)}:{line_number}: {label}"


if __name__ == "__main__":
    main()
