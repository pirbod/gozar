#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

import httpx


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed local Gorz demo identities and conversation.")
    parser.add_argument("--api", default="http://127.0.0.1:8090")
    args = parser.parse_args()

    with httpx.Client(base_url=args.api, timeout=10.0) as client:
        alice = client.post(
            "/api/gorz/identities",
            json={"display_name": "Ari Local", "device_label": "Laptop"},
        )
        alice.raise_for_status()
        blair = client.post(
            "/api/gorz/identities",
            json={"display_name": "Blair Demo", "device_label": "Phone"},
        )
        blair.raise_for_status()
        conversation = client.post(
            "/api/gorz/conversations",
            json={
                "title": "Local demo conversation",
                "participant_ids": [alice.json()["identity_id"], blair.json()["identity_id"]],
            },
        )
        conversation.raise_for_status()
        print(json.dumps({"identities": [alice.json(), blair.json()], "conversation": conversation.json()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

