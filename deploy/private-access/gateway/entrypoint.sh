#!/bin/sh
set -eu

: "${WIREGUARD_PRIVATE_KEY:?WIREGUARD_PRIVATE_KEY is required}"
: "${PROFILE_ADMIN_TOKEN:?PROFILE_ADMIN_TOKEN is required}"
: "${PROFILE_API_INTERNAL_URL:?PROFILE_API_INTERNAL_URL is required}"

WG_ADDRESS="${WG_ADDRESS:-10.77.0.1/24}"
SERVICE_CIDR="${SERVICE_CIDR:-10.88.0.0/24}"
SERVICE_HOST="${SERVICE_HOST:-10.88.0.10}"
SERVICE_PORT="${SERVICE_PORT:-8080}"

ip link add wg0 type wireguard
ip address add "$WG_ADDRESS" dev wg0
ip link set wg0 up

iptables -P FORWARD DROP
iptables -A FORWARD -i wg0 -d "$SERVICE_HOST" -p tcp --dport "$SERVICE_PORT" -j ACCEPT
iptables -A FORWARD -o wg0 -s "$SERVICE_CIDR" -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -t nat -A POSTROUTING -s "10.77.0.0/24" -d "$SERVICE_CIDR" -j MASQUERADE

while true; do
    peers="$(curl --fail --silent --show-error \
        -H "x-profile-admin-token: $PROFILE_ADMIN_TOKEN" \
        "$PROFILE_API_INTERNAL_URL/api/v1/admin/wireguard/peers")"
    config="$(mktemp)"
    chmod 0600 "$config"
    {
        printf '[Interface]\n'
        printf 'PrivateKey = %s\n' "$WIREGUARD_PRIVATE_KEY"
        printf 'ListenPort = 51820\n'
        printf '%s' "$peers" | jq -r '.[] | "[Peer]\nPublicKey = \(.public_key)\nAllowedIPs = \(.allowed_ip)\n"'
    } > "$config"
    wg syncconf wg0 "$config"
    rm -f "$config"
    sleep 5
done
