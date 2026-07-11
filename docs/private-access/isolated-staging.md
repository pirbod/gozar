# Isolated Private-Access Staging

This environment validates private access without exposing a consumer VPN or routing ordinary internet traffic.

## Boundaries

- The profile API is available only through HTTPS on host loopback port 8443.
- WireGuard accepts UDP only on host loopback port 51820.
- PostgreSQL has no host port.
- The synthetic service network is marked internal and has no external route.
- The gateway firewall permits only TCP port 8080 on the synthetic service.
- Profiles contain no IPv4 or IPv6 default route.
- Test identities, test keys, and synthetic data are required.
- This environment is staging. It is not a public deployment.

## Start

Requirements:

- Docker with Linux containers
- OpenSSL
- Android Studio with an API 30 or newer emulator

Generate staging secrets once:

```bash
./deploy/private-access/bootstrap.sh
```

Start the environment:

```bash
docker compose \
  --env-file deploy/private-access/.env.private-access \
  -f deploy/private-access/compose.yml \
  up -d --build --wait
```

Export the local certificate authority:

```bash
./deploy/private-access/export-ca.sh
```

Load the generated environment for the smoke test:

```bash
set -a
. deploy/private-access/.env.private-access
set +a
python3 scripts/private_access/smoke_test.py \
  --ca runtime/private-access-root.crt
```

The smoke result must report PostgreSQL storage, an active device, a valid profile, private routes, and the synthetic internal service.

Test packet transport through WireGuard and verify that the default route stays outside the tunnel:

```bash
./scripts/private_access/run_tunnel_smoke.sh
```

## Android Emulator

Install `runtime/private-access-root.crt` as a user CA on the dedicated emulator. The internal debug build trusts user-installed CAs. Release builds trust system CAs only.

Build the internal app with the generated signer pin:

```bash
cd android/gorz
./gradlew assembleInternalDebug \
  -PgorzProfileApiUrl=https://10.0.2.2:8443 \
  -PgorzIssuerPublicKey="$PROFILE_ISSUER_PUBLIC_KEY"
```

Install `app/build/outputs/apk/internal/debug/app-internal-debug.apk` on the isolated emulator.

In the app:

1. Open Settings.
2. Save the value of `PROFILE_ENROLLMENT_TOKEN` as the enrollment code.
3. Return Home and connect.
4. Open Resources.
5. Open Internal status.
6. Confirm that `http://10.88.0.10:8080` is reachable.
7. Confirm that ordinary internet traffic does not enter the tunnel.
8. Disconnect and verify that the internal service is no longer reachable.

## Operator Checks

List enrolled WireGuard peers without exposing device tokens:

```bash
curl --cacert runtime/private-access-root.crt \
  -H "x-profile-admin-token: $PROFILE_ADMIN_TOKEN" \
  https://localhost:8443/api/v1/admin/wireguard/peers
```

Pause new profile issuance:

```bash
curl --cacert runtime/private-access-root.crt \
  -X POST \
  -H "x-profile-admin-token: $PROFILE_ADMIN_TOKEN" \
  https://localhost:8443/api/v1/admin/access/pause
```

Resume issuance by replacing `pause` with `resume`.

## Stop And Delete

Stop while preserving PostgreSQL and certificate volumes:

```bash
docker compose \
  --env-file deploy/private-access/.env.private-access \
  -f deploy/private-access/compose.yml \
  down
```

Delete all staging data:

```bash
docker compose \
  --env-file deploy/private-access/.env.private-access \
  -f deploy/private-access/compose.yml \
  down -v
```

Delete `deploy/private-access/.env.private-access` when the staging environment is retired. Revoke enrolled devices before reusing a gateway.
