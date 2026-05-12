# Store-and-Forward Skeleton

`gozar-core` now includes a store-and-forward package skeleton for future delay-tolerant experiments.

## Included Pieces

- `StoreForwardPackage`
- `StoreForwardStatus`
- `StoreForwardQueue` trait
- `InMemoryStoreForwardQueue` reference skeleton

## Current Scope

This is not a complete offline delivery subsystem. It is a research placeholder that provides:

- package metadata
- TTL fields
- enqueue/dequeue hooks
- acknowledgement hooks
- unit-test coverage for the in-memory queue flow

## Not Included

- encryption-at-rest
- durable package replication
- anti-abuse controls for large untrusted payloads
- peer discovery for asynchronous delivery
- production retention policies

The skeleton exists so later milestones can experiment with delay-tolerant transport without changing the public crate layout again.