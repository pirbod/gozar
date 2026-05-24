# Local Demo Runbook

## Start Gorz Demo

```bash
make gorz-demo
```

## Start Profile API

```bash
make profile-demo
```

## Run Android Emulator Demo

Open `android/gorz` in Android Studio and run the app. Use `http://10.0.2.2:8095` for the Profile API URL.

## Health Checks

```bash
python scripts/local_health_report.py
python scripts/local_health_report.py --with-local-endpoints
```

## Common Failure Modes

| Failure | Likely Cause | Fix |
| --- | --- | --- |
| Profile API unavailable | Backend not running | Use offline demo or run `make profile-demo`. |
| Android cannot reach API | Wrong emulator URL | Use `http://10.0.2.2:8095`. |
| Docker service stale | Old containers | Run clean targets and restart. |
| VPN permission dialog appears | Android OS prompt | Accept manually for VPN lifecycle path. |

## Reset Local State

```bash
make gorz-clean
make profile-clean
make eval-clean
```

Use Android Settings screen to reset identity, audit, and diagnostics.

## Collect Local Logs

- Docker logs: `docker compose logs`.
- Runtime reports: `runtime/reports`.
- Profile runtime: `runtime/profile`.
- Gorz runtime: `runtime/gorz`.

## Generate Evidence Package

Open Android Evidence screen or Gorz Web incident flow and use the explicit export action.

## Stop Services

```bash
docker compose down -v
docker compose -f docker-compose.gorz.yml down -v
docker compose -f docker-compose.profile.yml down -v
```
