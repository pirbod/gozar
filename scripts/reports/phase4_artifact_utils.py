#!/usr/bin/env python3
from __future__ import annotations

import json
import struct
import zlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PLACEHOLDER_LABEL = "PLACEHOLDER - screenshot capture pending"

ANDROID_SCREENSHOTS = [
    ("phase4-home.png", "Android Home screen"),
    ("phase4-connect-flow.png", "Android offline connect flow"),
    ("phase4-session.png", "Android session dashboard"),
    ("phase4-confidence.png", "Android confidence screen"),
    ("phase4-route-policy.png", "Android route policy screen"),
    ("phase4-diagnostics.png", "Android diagnostics screen"),
    ("phase4-evidence.png", "Android Evidence Package V2 screen"),
    ("phase4-safety-pause.png", "Android safety pause screen"),
    ("phase4-audit.png", "Android audit timeline"),
    ("phase4-settings.png", "Android settings screen"),
    ("phase4-storage-mode.png", "Android storage mode screen"),
    ("phase4-emulator-smoke-result.png", "Android emulator smoke result"),
]

PLATFORM_SCREENSHOTS = [
    ("phase4-github-actions.png", "GitHub Actions workflow view"),
    ("phase4-terraform-validate.png", "Terraform validation output"),
    ("phase4-kubernetes-manifests.png", "Kubernetes manifest validation"),
    ("phase4-prometheus-alerts.png", "Prometheus alert rules"),
    ("phase4-grafana-dashboard.png", "Grafana dashboard"),
    ("phase4-siem-detection-report.png", "SIEM detection report"),
    ("phase4-incident-summary.png", "Deterministic incident summary"),
    ("phase4-production-readiness-report.png", "Production readiness report"),
]

FONT: dict[str, tuple[str, ...]] = {
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "/": ("00001", "00010", "00100", "01000", "10000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
}


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat()


def write_placeholder_png(path: Path, title: str, subtitle: str, width: int = 1280, height: int = 720) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pixels = bytearray()
    background = (245, 247, 250)
    band = (229, 234, 242)
    border = (87, 96, 111)
    accent = (185, 28, 28)
    text = (17, 24, 39)
    muted = (75, 85, 99)

    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            color = background
            if height // 2 - 105 <= y <= height // 2 + 105:
                color = band
            if x < 14 or x >= width - 14 or y < 14 or y >= height - 14:
                color = border
            row.extend(color)
        pixels.extend(row)

    lines = [
        (PLACEHOLDER_LABEL.upper(), 5, accent),
        (title.upper(), 4, text),
        (subtitle.upper(), 3, muted),
    ]
    current_y = height // 2 - 82
    for line, scale, color in lines:
        draw_centered_text(pixels, width, height, current_y, line, scale, color)
        current_y += 78 if scale >= 5 else 56

    png = png_bytes(width, height, bytes(pixels))
    path.write_bytes(png)


def draw_centered_text(
    pixels: bytearray,
    width: int,
    height: int,
    y: int,
    text: str,
    scale: int,
    color: tuple[int, int, int],
) -> None:
    safe_text = "".join(ch if ch.upper() in FONT else " " for ch in text.upper())
    text_width = max(0, len(safe_text) * 6 * scale - scale)
    x = max(24, (width - text_width) // 2)
    draw_text(pixels, width, height, x, y, safe_text, scale, color)


def draw_text(
    pixels: bytearray,
    width: int,
    height: int,
    x: int,
    y: int,
    text: str,
    scale: int,
    color: tuple[int, int, int],
) -> None:
    cursor = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit != "1":
                    continue
                draw_block(pixels, width, height, cursor + gx * scale, y + gy * scale, scale, color)
        cursor += 6 * scale


def draw_block(
    pixels: bytearray,
    width: int,
    height: int,
    x: int,
    y: int,
    size: int,
    color: tuple[int, int, int],
) -> None:
    for yy in range(y, min(y + size, height)):
        if yy < 0:
            continue
        for xx in range(x, min(x + size, width)):
            if xx < 0:
                continue
            offset = yy * (1 + width * 3) + 1 + xx * 3
            pixels[offset : offset + 3] = bytes(color)


def png_bytes(width: int, height: int, scanlines: bytes) -> bytes:
    def chunk(name: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(scanlines, 9)) + chunk(b"IEND", b"")


def write_screenshot_readme(root: Path) -> None:
    docs_dir = root / "docs" / "vpn-product" / "images" / "phase4"
    report_dir = root / "runtime" / "reports" / "screenshots" / "phase4"
    generated = utc_timestamp()
    records: dict[str, dict[str, str]] = {}

    for filename, related in ANDROID_SCREENSHOTS + PLATFORM_SCREENSHOTS:
        records[filename] = {
            "filename": filename,
            "status": "REAL" if (docs_dir / filename).exists() else "MISSING",
            "captureMethod": "Manual or existing image",
            "lastUpdated": generated if (docs_dir / filename).exists() else "n/a",
            "related": related,
        }

    for report_name in ["screenshot-capture-report.json", "platform-screenshot-report.json"]:
        report_path = report_dir / report_name
        if not report_path.exists():
            continue
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        for item in payload.get("screenshots", []):
            filename = str(item.get("filename", ""))
            if filename in records:
                records[filename].update(
                    {
                        "status": str(item.get("status", records[filename]["status"])),
                        "captureMethod": str(item.get("captureMethod", records[filename]["captureMethod"])),
                        "lastUpdated": str(item.get("lastUpdated", records[filename]["lastUpdated"])),
                        "related": str(item.get("related", records[filename]["related"])),
                    }
                )

    lines = [
        "# Phase 4 Screenshot Status",
        "",
        f"Last updated: {generated}",
        "",
        "Screenshots are either real captures or visibly labelled placeholders. Placeholder images are not product proof; they mark capture work that still needs a real emulator, browser, or desktop capture run.",
        "",
        "| Screenshot filename | Status | Capture method | Last updated | Related screen or report |",
        "| --- | --- | --- | --- | --- |",
    ]
    for filename in [item[0] for item in ANDROID_SCREENSHOTS + PLATFORM_SCREENSHOTS]:
        record = records[filename]
        lines.append(
            f"| `{filename}` | {record['status']} | {record['captureMethod']} | {record['lastUpdated']} | {record['related']} |"
        )
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def status_from_report(path: Path, default: str = "MISSING") -> str:
    payload = load_json(path)
    return str(payload.get("status", default))
