#!/usr/bin/env bash
set -euo pipefail

latency_ms="${1:-250}"
target_service="${2:-relay}"

echo "Applying ${latency_ms}ms one-way delay to ${target_service} using tc netem."
docker compose exec -T "${target_service}" tc qdisc replace dev eth0 root netem delay "${latency_ms}ms"
echo "Run scripts/simulations/clear-netem.sh ${target_service} to remove the impairment."