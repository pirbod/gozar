#!/usr/bin/env bash
set -euo pipefail

duration_seconds="${1:-20}"

echo "Stopping gateway for ${duration_seconds}s to simulate a gateway outage in a controlled lab stack."
docker compose stop gateway
trap 'docker compose start gateway >/dev/null 2>&1 || true' EXIT
sleep "${duration_seconds}"
docker compose start gateway