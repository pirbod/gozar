#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN_PATHS = [
    ROOT / "README.md",
    ROOT / "docs" / "vpn-product",
    ROOT / "python" / "profile_api",
    ROOT / "scripts" / "profile",
]
UNSAFE_PATTERNS = [
    "un" + "blockable",
    "un" + "detectable",
    "stealth " + "VPN",
    "bypass " + "anything",
    "public relay " + "discovery",
    "traffic " + "camouflage",
]


def main() -> None:
    violations: list[str] = []
    for path in _iter_files():
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            if _is_safety_disclaimer(lowered):
                continue
            for pattern in UNSAFE_PATTERNS:
                if pattern.lower() not in lowered:
                    continue
                violations.append(f"{path.relative_to(ROOT)} contains unsafe phrase: {pattern}")
                violations[-1] += f" on line {line_number}"
    if violations:
        raise SystemExit("\n".join(violations))


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for path in SCAN_PATHS:
        if path.is_file():
            files.append(path)
            continue
        files.extend(
            item
            for item in path.rglob("*")
            if item.is_file()
            and item.suffix in {".md", ".py", ".toml", ".yml", ".yaml"}
            and item.name != Path(__file__).name
        )
    return files


def _is_safety_disclaimer(line: str) -> bool:
    safe_prefixes = ("no ", "not ", "never ", "without ")
    stripped = line.strip().removeprefix("-").strip()
    return any(stripped.startswith(prefix) for prefix in safe_prefixes)


if __name__ == "__main__":
    main()
