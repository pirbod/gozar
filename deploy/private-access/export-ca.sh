#!/bin/sh
set -eu

root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
deployment="$root/deploy/private-access"
env_file="$deployment/.env.private-access"
output="$root/runtime/private-access-root.crt"

mkdir -p "$(dirname "$output")"
docker compose --env-file "$env_file" -f "$deployment/compose.yml" \
    cp caddy:/data/caddy/pki/authorities/local/root.crt "$output"
chmod 0644 "$output"
echo "$output"
