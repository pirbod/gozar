#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import urllib.request
from pathlib import Path
from typing import Callable

REPOSITORY = "pirbod/gozar"
GITHUB_ARCHIVE_BASE = f"https://github.com/{REPOSITORY}/archive/refs/tags"
URL_PATTERN = re.compile(r'^\s*url\s+".*"$', re.MULTILINE)
SHA_PATTERN = re.compile(r'^\s*sha256\s+".*"$', re.MULTILINE)


def validate_tag(tag: str) -> str:
    if not tag.startswith("v"):
        raise ValueError("tag must start with v, for example v0.1.0")
    if tag == "v" or any(char.isspace() for char in tag):
        raise ValueError("tag must be a compact release tag such as v0.1.0")
    return tag


def tarball_url_for_tag(tag: str) -> str:
    validate_tag(tag)
    return f"{GITHUB_ARCHIVE_BASE}/{tag}.tar.gz"


def download_tarball(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_formula_fields(template: str, url: str, sha256: str) -> str:
    updated, url_count = URL_PATTERN.subn(f'  url "{url}"', template, count=1)
    updated, sha_count = SHA_PATTERN.subn(f'  sha256 "{sha256}"', updated, count=1)

    if url_count != 1:
        raise ValueError("formula template must contain one url line")
    if sha_count != 1:
        raise ValueError("formula template must contain one sha256 line")

    return updated


def prepare_formula(
    tag: str,
    template: str,
    downloader: Callable[[str], bytes] = download_tarball,
) -> tuple[str, str, str]:
    url = tarball_url_for_tag(tag)
    archive = downloader(url)
    digest = sha256_bytes(archive)
    return replace_formula_fields(template, url, digest), url, digest


def print_next_steps(output: Path, tag: str) -> None:
    print(f"Prepared Homebrew formula for {tag}: {output}")
    print("")
    print("Next steps for pirbod/homebrew-tap:")
    print("  mkdir -p Formula")
    print(f"  cp {output} Formula/gorz.rb")
    print("  git add Formula/gorz.rb")
    print(f'  git commit -m "Update gorz formula to {tag}"')
    print("  git push origin main")
    print("")
    print("Install test:")
    print("  brew update")
    print("  brew install pirbod/tap/gorz")
    print("  gorz doctor")
    print("  gorz demo")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a Homebrew formula for a Gorz release.")
    parser.add_argument("--tag", required=True, help="Release tag, for example v0.1.0")
    parser.add_argument(
        "--formula-template",
        default="packaging/homebrew/Formula/gorz.rb",
        help="Path to the formula template",
    )
    parser.add_argument("--output", default="/tmp/gorz.rb", help="Path to write the prepared formula")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    try:
        tag = validate_tag(args.tag)
        template_path = Path(args.formula_template)
        output_path = Path(args.output)
        prepared, url, digest = prepare_formula(tag, template_path.read_text(encoding="utf-8"))
        output_path.write_text(prepared, encoding="utf-8")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Tarball: {url}")
    print(f"SHA-256: {digest}")
    print_next_steps(output_path, tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
