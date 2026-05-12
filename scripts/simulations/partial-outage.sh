#!/usr/bin/env bash
set -euo pipefail

duration_seconds="${1:-20}"

echo "Pausing relay for ${duration_seconds}s to simulate a partial outage in a controlled lab stack."
docker compose pause relay
trap 'docker compose unpause relay >/dev/null 2>&1 || true' EXIT
sleep "${duration_seconds}"
docker compose unpause relay