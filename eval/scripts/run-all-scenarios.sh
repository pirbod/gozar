#!/usr/bin/env bash
set -euo pipefail

# Thin wrapper used by local experiments; CI calls the same runner in smoke mode.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

python3 eval/scripts/eval_runner.py run-all "$@"
