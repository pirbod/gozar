#!/usr/bin/env python3
from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "--android-only"]
    runpy.run_path(str(ROOT / "scripts" / "check_safety_wording.py"), run_name="__main__")
