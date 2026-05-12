#!/usr/bin/env bash
set -euo pipefail

duration_seconds="${1:-20}"

echo "Stopping relay for ${duration_seconds}s to simulate a relay failure in a controlled lab stack."
docker compose stop relay
trap 'docker compose start relay >/dev/null 2>&1 || true' EXIT
sleep "${duration_seconds}"
docker compose start relay