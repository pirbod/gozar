#!/usr/bin/env bash
set -euo pipefail

loss_percent="${1:-15}"
target_service="${2:-relay}"

echo "Applying ${loss_percent}% packet loss to ${target_service} using tc netem."
docker compose exec -T "${target_service}" tc qdisc replace dev eth0 root netem loss "${loss_percent}%"
echo "Run scripts/simulations/clear-netem.sh ${target_service} to remove the impairment."