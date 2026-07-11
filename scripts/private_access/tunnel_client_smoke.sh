#!/bin/sh
set -eu

: "${PROFILE_ENROLLMENT_TOKEN:?PROFILE_ENROLLMENT_TOKEN is required}"
api_url="${PROFILE_API_URL:-https://gozar.internal:8443}"
ca_file="${PROFILE_CA_FILE:-/root.crt}"

private_key="$(wg genkey)"
public_key="$(printf '%s' "$private_key" | wg pubkey)"
payload="$(jq -n --arg key "$public_key" '{
    display_name: "WireGuard tunnel check",
    app_version: "smoke",
    device_public_key: $key,
    wireguard_public_key: $key
}')"
enrollment="$(printf '%s' "$payload" | curl --fail --silent --show-error \
    --cacert "$ca_file" \
    -H "content-type: application/json" \
    -H "x-gozar-enrollment-token: $PROFILE_ENROLLMENT_TOKEN" \
    --data-binary @- \
    "$api_url/api/v1/enrollment")"
device_token="$(printf '%s' "$enrollment" | jq -er '.device_token')"
profile="$(printf '{}' | curl --fail --silent --show-error \
    --cacert "$ca_file" \
    -H "content-type: application/json" \
    -H "authorization: Bearer $device_token" \
    --data-binary @- \
    "$api_url/api/v1/access-profiles")"

client_address="$(printf '%s' "$profile" | jq -er '.client_address')"
gateway_public_key="$(printf '%s' "$profile" | jq -er '.gateway_public_key')"
routes="$(printf '%s' "$profile" | jq -er '.approved_routes[]')"

config="$(mktemp)"
trap 'rm -f "$config"' EXIT
chmod 0600 "$config"
{
    printf '[Interface]\nPrivateKey = %s\n\n' "$private_key"
    printf '[Peer]\nPublicKey = %s\n' "$gateway_public_key"
    printf 'Endpoint = gateway:51820\n'
    printf 'AllowedIPs = %s\n' "$(printf '%s\n' "$routes" | paste -sd, -)"
    printf 'PersistentKeepalive = 25\n'
} > "$config"

ip link add wg0 type wireguard
wg setconf wg0 "$config"
ip address add "$client_address/32" dev wg0
ip link set wg0 up
printf '%s\n' "$routes" | while IFS= read -r route; do
    ip route add "$route" dev wg0
done

sleep 7
curl --fail --silent --show-error --max-time 10 http://10.88.0.10:8080/ | grep -q "Private staging service is reachable"

default_route="$(ip route get 1.1.1.1 2>/dev/null || true)"
if printf '%s' "$default_route" | grep -q "dev wg0"; then
    echo "default traffic entered the private tunnel" >&2
    exit 1
fi

echo "WireGuard private-service tunnel: pass"
