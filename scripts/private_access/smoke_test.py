from __future__ import annotations

import argparse
import base64
import ipaddress
import json
import os
import ssl
import urllib.request
from typing import Any


def request(
    base_url: str,
    path: str,
    *,
    context: ssl.SSLContext,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=body,
        method=method,
        headers={"content-type": "application/json", **(headers or {})},
    )
    with urllib.request.urlopen(req, context=context, timeout=10) as response:
        parsed = json.loads(response.read())
    if not isinstance(parsed, dict):
        raise RuntimeError(f"{path} did not return an object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate isolated private-access staging")
    parser.add_argument("--base-url", default="https://localhost:8443")
    parser.add_argument("--ca", required=True)
    parser.add_argument(
        "--enrollment-token",
        default=os.getenv("PROFILE_ENROLLMENT_TOKEN"),
    )
    args = parser.parse_args()
    if not args.enrollment_token:
        parser.error("--enrollment-token or PROFILE_ENROLLMENT_TOKEN is required")

    context = ssl.create_default_context(cafile=args.ca)
    ready = request(args.base_url, "/readyz", context=context)
    if ready.get("status") != "ready" or ready.get("storage") != "postgresql":
        raise RuntimeError(f"unexpected readiness response: {ready}")

    public_key = base64.b64encode(os.urandom(32)).decode()
    enrollment = request(
        args.base_url,
        "/api/v1/enrollment",
        context=context,
        method="POST",
        headers={"x-gozar-enrollment-token": args.enrollment_token},
        payload={
            "display_name": "Isolated staging check",
            "app_version": "smoke",
            "device_public_key": public_key,
            "wireguard_public_key": public_key,
        },
    )
    token = str(enrollment["device_token"])
    auth = {"authorization": f"Bearer {token}"}
    device = request(args.base_url, "/api/v1/me", context=context, headers=auth)
    profile = request(
        args.base_url,
        "/api/v1/access-profiles",
        context=context,
        method="POST",
        headers=auth,
        payload={},
    )
    validation = request(
        args.base_url,
        f"/api/v1/access-profiles/{profile['profile_id']}/validate",
        context=context,
        method="POST",
        headers=auth,
        payload={},
    )

    routes = [ipaddress.ip_network(route, strict=True) for route in profile["approved_routes"]]
    if not routes or any(not route.is_private or route.prefixlen == 0 for route in routes):
        raise RuntimeError("profile contains a route outside private staging")
    if "0.0.0.0/0" in profile["approved_routes"] or "::/0" in profile["approved_routes"]:
        raise RuntimeError("profile contains a default route")
    services = profile.get("approved_services", [])
    if not services:
        raise RuntimeError("profile contains no approved services")
    if any(
        not ipaddress.ip_address(service["host"]).is_private
        or not any(ipaddress.ip_address(service["host"]) in route for route in routes)
        for service in services
    ):
        raise RuntimeError("approved service is outside the signed route set")
    if device.get("status") != "active" or validation.get("valid") is not True:
        raise RuntimeError("device or profile validation failed")

    print(
        json.dumps(
            {
                "status": "pass",
                "storage": ready["storage"],
                "device_status": device["status"],
                "profile_status": validation["status"],
                "approved_routes": profile["approved_routes"],
                "approved_services": [service["name"] for service in services],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
