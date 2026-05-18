#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import httpx


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a redacted local Gorz demo incident.")
    parser.add_argument("--api", default="http://127.0.0.1:8090")
    parser.add_argument("--output", default="runtime/gorz/demo-incident.json")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with httpx.Client(base_url=args.api, timeout=10.0) as client:
        alice = client.post(
            "/api/gorz/identities",
            json={"display_name": "Export Alice", "device_label": "Laptop"},
        )
        alice.raise_for_status()
        bob = client.post(
            "/api/gorz/identities",
            json={"display_name": "Export Bob", "device_label": "Phone"},
        )
        bob.raise_for_status()
        conversation = client.post(
            "/api/gorz/conversations",
            json={
                "title": "Incident export demo",
                "participant_ids": [alice.json()["identity_id"], bob.json()["identity_id"]],
            },
        )
        conversation.raise_for_status()
        message = client.post(
            "/api/gorz/messages",
            json={
                "conversation_id": conversation.json()["conversation_id"],
                "sender_id": alice.json()["identity_id"],
                "body": "export demo plaintext must not appear",
                "scenario": "blocked",
            },
        )
        message.raise_for_status()
        incident = client.post(f"/api/gorz/incidents/from-message/{message.json()['message_id']}")
        incident.raise_for_status()
        download = client.get(f"/api/gorz/incidents/{incident.json()['incident_id']}/download")
        download.raise_for_status()
        output.write_text(download.text, encoding="utf-8")

    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

