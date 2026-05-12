# Signed Relay Directory

The control plane now exposes a signed relay directory at `/api/v1/relay-directory`.

## Purpose

The directory gives the client a research-safe view of known relay ingress points so the client can:

- evaluate relay freshness
- enrich path scoring
- log which relay metadata influenced route choice

## Response Shape

Each directory response includes:

- `request_nonce`
- `response_nonce`
- `issued_at_unix`
- `directory.requester_node_id`
- `directory.valid_for_seconds`
- `directory.entries[]`
- `signature`

Each relay entry includes:

- relay id
- relay ingress address
- gateway address
- observed timestamp
- status
- queue limit
- research-gateway support flag
- relay feature list from heartbeat registration

## Signing Model

The response is signed with the same HMAC secret used for demo control messages. This keeps the prototype internally consistent while remaining clearly non-production.

The client verifies:

- request nonce matches the issued request
- requester node id matches the local node
- response is still fresh
- response nonce has not been replayed locally
- directory signature matches the expected signature base

## Research Notes

The directory is intentionally simple. It does not implement distributed trust, federation, or public enrollment. Those topics are left for future research and are out of scope for this lab prototype.