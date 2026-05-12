#!/usr/bin/env bash
set -euo pipefail

# The pause/unpause loop emulates intermittent connectivity without touching
# host firewall rules or any external network path.

service="${1:-relay}"
duration_seconds="${2:-20}"
cycle_seconds="${3:-3}"

log() {
  printf '[eval:intermittent] %s\n' "$*"
}

end_at=$((SECONDS + duration_seconds))
log "starting intermittent connectivity service=$service duration=${duration_seconds}s cycle=${cycle_seconds}s"

while (( SECONDS < end_at )); do
  docker compose pause "$service" >/dev/null 2>&1 || true
  sleep "$cycle_seconds"
  docker compose unpause "$service" >/dev/null 2>&1 || true
  sleep "$cycle_seconds"
done

docker compose unpause "$service" >/dev/null 2>&1 || true
log "intermittent connectivity completed service=$service"
