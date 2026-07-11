#!/bin/sh
set -eu

root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
deployment="$root/deploy/private-access"
env_file="$deployment/.env.private-access"

if [ -e "$env_file" ]; then
    echo "$env_file already exists; refusing to overwrite it." >&2
    exit 1
fi

docker build -f "$deployment/docker/Dockerfile.profile-api" -t gozar-private-access-profile-api "$root"
docker build -f "$deployment/docker/Dockerfile.gateway" -t gozar-private-access-gateway "$root"

issuer_private_key="$(docker run --rm gozar-private-access-profile-api python -c 'import base64; from nacl.signing import SigningKey; print(base64.b64encode(bytes(SigningKey.generate())).decode())')"
issuer_public_key="$(printf '%s' "$issuer_private_key" | docker run --rm -i gozar-private-access-profile-api python -c 'import base64, sys; from nacl.signing import SigningKey; key=base64.b64decode(sys.stdin.read()); print(base64.b64encode(bytes(SigningKey(key).verify_key)).decode())')"
gateway_private_key="$(docker run --rm --entrypoint wg gozar-private-access-gateway genkey)"
gateway_public_key="$(printf '%s' "$gateway_private_key" | docker run --rm -i --entrypoint wg gozar-private-access-gateway pubkey)"

umask 077
cat > "$env_file" <<EOF
POSTGRES_PASSWORD=$(openssl rand -hex 32)
PROFILE_ADMIN_TOKEN=$(openssl rand -hex 32)
PROFILE_ENROLLMENT_TOKEN=$(openssl rand -hex 32)
PROFILE_DEVICE_TOKEN_PEPPER=$(openssl rand -hex 32)
PROFILE_ISSUER_PRIVATE_KEY=$issuer_private_key
PROFILE_ISSUER_PUBLIC_KEY=$issuer_public_key
PROFILE_GATEWAY_PRIVATE_KEY=$gateway_private_key
PROFILE_GATEWAY_PUBLIC_KEY=$gateway_public_key
PROFILE_GATEWAY_ENDPOINT=10.0.2.2:51820
EOF

echo "Created $env_file"
echo "Start with: docker compose --env-file $env_file -f $deployment/compose.yml up -d --build"
