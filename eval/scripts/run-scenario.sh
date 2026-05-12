#!/usr/bin/env bash
set -euo pipefail

# Thin wrapper so researchers can invoke one scenario without remembering the
# Python runner subcommand.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

if [[ $# -lt 1 ]]; then
  printf 'Usage: eval/scripts/run-scenario.sh eval/scenarios/name.yaml [--ci-safe]\n' >&2
  exit 2
fi

python3 eval/scripts/eval_runner.py run-scenario "$@"
