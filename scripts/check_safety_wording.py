#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BLOCKED_PHRASES = [
    "un" + "blockable",
    "un" + "detectable",
    "stealth " + "VPN",
    "bypass " + "anything",
    "traffic " + "camouflage",
    "public relay " + "discovery",
    "hidden " + "tunnel",
    "evade " + "censorship",
    "anti-" + "blocking",
]

REQUIRED_SAFETY_PHRASES = [
    "not a circumvention tool",
    "no public relay discovery",
    "no public network probing",
    "not production secure",
]

SCAN_TARGETS = [
    ROOT / "README.md",
    ROOT / "docs",
    ROOT / "python",
    ROOT / "scripts",
    ROOT / "android",
    ROOT / ".github" / "workflows",
    ROOT / "Makefile",
]

ANDROID_TARGETS = [
    ROOT / "android",
]

SCAN_SUFFIXES = {".md", ".py", ".kt", ".xml", ".yml", ".yaml"}
CHECKER_FILENAMES = {
    "check_safety_wording.py",
    "check_android_safety_wording.py",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Check prototype safety wording boundaries.")
    parser.add_argument("--android-only", action="store_true", help="Scan only Android project files.")
    args = parser.parse_args()

    targets = ANDROID_TARGETS if args.android_only else SCAN_TARGETS
    files = _iter_files(targets)
    violations = _find_blocked_phrase_violations(files)
    if not args.android_only:
        violations.extend(_find_missing_required_phrases(files))
    if violations:
        raise SystemExit("\n".join(violations))


def _iter_files(targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        if not target.exists():
            continue
        if target.is_file():
            if _should_scan_file(target):
                files.append(target)
            continue
        files.extend(item for item in target.rglob("*") if _should_scan_file(item))
    return sorted(set(files))


def _should_scan_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.name in CHECKER_FILENAMES:
        return False
    if path.name == "Makefile":
        return True
    if path.suffix not in SCAN_SUFFIXES:
        return False
    if ".github/workflows" in path.as_posix():
        return path.suffix in {".yml", ".yaml"}
    if "/python/" in path.as_posix() or "/scripts/" in path.as_posix():
        return path.suffix == ".py"
    return True


def _find_blocked_phrase_violations(files: list[Path]) -> list[str]:
    violations: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            for phrase in BLOCKED_PHRASES:
                phrase_lower = phrase.lower()
                if phrase_lower not in lowered:
                    continue
                if _is_allowed_safety_phrase_line(lowered, phrase_lower):
                    continue
                violations.append(
                    f"{path.relative_to(ROOT)} contains blocked safety wording '{phrase}' on line {line_number}"
                )
    return violations


def _find_missing_required_phrases(files: list[Path]) -> list[str]:
    corpus = "\n".join(path.read_text(encoding="utf-8").lower() for path in files)
    return [
        f"missing required safety phrase: {phrase}"
        for phrase in REQUIRED_SAFETY_PHRASES
        if phrase not in corpus
    ]


def _is_allowed_safety_phrase_line(lowered_line: str, phrase_lower: str) -> bool:
    if phrase_lower == "public relay discovery" and "no public relay discovery" in lowered_line:
        return True
    return False


if __name__ == "__main__":
    main()
