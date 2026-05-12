#!/usr/bin/env bash
set -euo pipefail

# Apply netem inside one Compose service only; this keeps impairments local
# to the lab stack and makes cleanup straightforward.

log() {
  printf '[eval:netem] %s\n' "$*"
}

usage() {
  cat <<'USAGE'
Usage:
  eval/scripts/apply-netem.sh SERVICE latency MS
  eval/scripts/apply-netem.sh SERVICE jitter DELAY_MS JITTER_MS
  eval/scripts/apply-netem.sh SERVICE loss PERCENT
  eval/scripts/apply-netem.sh SERVICE bandwidth RATE

Examples:
  eval/scripts/apply-netem.sh relay latency 200
  eval/scripts/apply-netem.sh relay loss 5
  eval/scripts/apply-netem.sh relay bandwidth 512kbit
USAGE
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "missing required command: $1"
    exit 1
  fi
}

if [[ $# -lt 3 ]]; then
  usage
  exit 2
fi

require_command docker

service="$1"
impairment="$2"
value="$3"
extra="${4:-}"

case "$impairment" in
  latency)
    qdisc=(tc qdisc replace dev eth0 root netem delay "${value}ms")
    ;;
  jitter)
    if [[ -z "$extra" ]]; then
      log "jitter requires DELAY_MS and JITTER_MS"
      exit 2
    fi
    qdisc=(tc qdisc replace dev eth0 root netem delay "${value}ms" "${extra}ms")
    ;;
  loss)
    qdisc=(tc qdisc replace dev eth0 root netem loss "${value}%")
    ;;
  bandwidth)
    qdisc=(tc qdisc replace dev eth0 root netem rate "$value")
    ;;
  *)
    log "unsupported impairment: $impairment"
    usage
    exit 2
    ;;
esac

log "applying $impairment=$value${extra:+,$extra} to service=$service"
docker compose exec -T "$service" "${qdisc[@]}"
log "applied impairment; clear it with eval/scripts/clear-netem.sh $service"
