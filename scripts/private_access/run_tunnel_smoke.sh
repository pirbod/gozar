#!/bin/sh
set -eu

root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
env_file="$root/deploy/private-access/.env.private-access"
set -a
. "$env_file"
set +a

docker run --rm \
    --network gozar-private-access_control \
    --cap-add NET_ADMIN \
    -e PROFILE_ENROLLMENT_TOKEN \
    -v "$root/runtime/private-access-root.crt:/root.crt:ro" \
    -v "$root/scripts/private_access/tunnel_client_smoke.sh:/tunnel_client_smoke.sh:ro" \
    --entrypoint /bin/sh \
    gozar-private-access-gateway \
    /tunnel_client_smoke.sh
