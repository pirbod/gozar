#!/usr/bin/env bash
set -euo pipefail

target_service="${1:-relay}"

echo "Clearing tc netem settings on ${target_service}."
docker compose exec -T "${target_service}" tc qdisc del dev eth0 root || true