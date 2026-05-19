from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "gorz" / "prepare_homebrew_release.py"
SPEC = importlib.util.spec_from_file_location("prepare_homebrew_release", SCRIPT_PATH)
assert SPEC is not None
prepare_homebrew_release = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(prepare_homebrew_release)


class PrepareHomebrewReleaseTest(unittest.TestCase):
    def test_tag_validation_requires_v_prefix(self) -> None:
        self.assertEqual(prepare_homebrew_release.validate_tag("v0.1.0"), "v0.1.0")
        with self.assertRaises(ValueError):
            prepare_homebrew_release.validate_tag("0.1.0")
        with self.assertRaises(ValueError):
            prepare_homebrew_release.validate_tag("v")

    def test_generated_url_format(self) -> None:
        self.assertEqual(
            prepare_homebrew_release.tarball_url_for_tag("v0.1.0"),
            "https://github.com/pirbod/gozar/archive/refs/tags/v0.1.0.tar.gz",
        )

    def test_formula_replacement_with_fake_sha(self) -> None:
        template = (
            "class Gorz < Formula\n"
            '  url "https://example.invalid/old.tar.gz"\n'
            '  sha256 "REPLACE_WITH_RELEASE_TARBALL_SHA256"\n'
            "end\n"
        )
        updated = prepare_homebrew_release.replace_formula_fields(
            template,
            "https://github.com/pirbod/gozar/archive/refs/tags/v0.2.0.tar.gz",
            "fake-sha",
        )
        self.assertIn('url "https://github.com/pirbod/gozar/archive/refs/tags/v0.2.0.tar.gz"', updated)
        self.assertIn('sha256 "fake-sha"', updated)
        self.assertNotIn("REPLACE_WITH_RELEASE_TARBALL_SHA256", updated)

    def test_prepare_formula_uses_injected_downloader(self) -> None:
        calls: list[str] = []

        def fake_downloader(url: str) -> bytes:
            calls.append(url)
            return b"fake archive bytes"

        prepared, url, digest = prepare_homebrew_release.prepare_formula(
            "v0.3.0",
            (
                "class Gorz < Formula\n"
                '  url "https://example.invalid/old.tar.gz"\n'
                '  sha256 "old"\n'
                "end\n"
            ),
            downloader=fake_downloader,
        )

        self.assertEqual(calls, ["https://github.com/pirbod/gozar/archive/refs/tags/v0.3.0.tar.gz"])
        self.assertEqual(url, calls[0])
        self.assertEqual(digest, prepare_homebrew_release.sha256_bytes(b"fake archive bytes"))
        self.assertIn(f'sha256 "{digest}"', prepared)


if __name__ == "__main__":
    unittest.main()
