#!/usr/bin/env bash
set -euo pipefail

# Clearing is intentionally tolerant because cleanup should be safe to call
# before containers exist, after failures, or multiple times in a row.

service="${1:-relay}"

if ! command -v docker >/dev/null 2>&1; then
  printf '[eval:netem] docker is not available; nothing to clear\n'
  exit 0
fi

printf '[eval:netem] clearing netem on service=%s\n' "$service"
docker compose exec -T "$service" tc qdisc del dev eth0 root >/dev/null 2>&1 || true
printf '[eval:netem] clear completed for service=%s\n' "$service"
