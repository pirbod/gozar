#!/usr/bin/env python3
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "android" / "gorz" / "app" / "src" / "main" / "AndroidManifest.xml"
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"

ALLOWED_PERMISSIONS = {
    "android.permission.INTERNET",
    "android.permission.FOREGROUND_SERVICE",
}

BLOCKED_PERMISSIONS = {
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.READ_PHONE_NUMBERS",
    "android.permission.READ_PHONE_STATE",
    "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA",
}

VPN_SERVICE_PERMISSION = "android.permission.BIND_VPN_SERVICE"


def main() -> None:
    if not MANIFEST.exists():
        raise SystemExit(f"FAIL: missing manifest: {MANIFEST.relative_to(ROOT)}")

    root = ET.parse(MANIFEST).getroot()
    permissions = sorted(
        permission.attrib.get(f"{ANDROID_NS}name", "")
        for permission in root.findall("uses-permission")
        if permission.attrib.get(f"{ANDROID_NS}name")
    )
    blocked = sorted(set(permissions) & BLOCKED_PERMISSIONS)

    service_permissions = sorted(
        service.attrib.get(f"{ANDROID_NS}permission", "")
        for service in root.findall("./application/service")
        if service.attrib.get(f"{ANDROID_NS}permission")
    )
    bind_vpn_service_ok = VPN_SERVICE_PERMISSION in service_permissions and VPN_SERVICE_PERMISSION not in permissions
    unexpected = sorted(set(permissions) - ALLOWED_PERMISSIONS - BLOCKED_PERMISSIONS)

    print("Android manifest permission check")
    print(f"Permissions found: {', '.join(permissions) if permissions else 'none'}")
    print(f"Service permissions found: {', '.join(service_permissions) if service_permissions else 'none'}")

    failures: list[str] = []
    if blocked:
        failures.append(f"blocked permissions present: {', '.join(blocked)}")
    if unexpected:
        failures.append(f"unexpected manifest permissions present: {', '.join(unexpected)}")
    if not bind_vpn_service_ok:
        failures.append("BIND_VPN_SERVICE must be scoped to the VPN service, not uses-permission")

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("PASS")


if __name__ == "__main__":
    main()
