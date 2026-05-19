from __future__ import annotations

from profile_api.crypto import (
    decrypt_for_device_for_demo_client,
    encrypt_for_device,
    generate_device_keypair,
    generate_issuer_signing_keypair,
    public_key_fingerprint,
    sign_envelope,
    verify_envelope_signature,
)


def test_device_keypair_generation() -> None:
    public_key, private_key = generate_device_keypair()
    assert public_key != private_key
    assert public_key_fingerprint(public_key).startswith("pkh_")


def test_encrypt_decrypt_demo_payload() -> None:
    public_key, private_key = generate_device_keypair()
    payload = {"profile_id": "prof_demo", "routing": {"mode": "demo_split_tunnel"}}
    encrypted = encrypt_for_device(payload, public_key)
    assert "demo_split_tunnel" not in encrypted
    assert decrypt_for_device_for_demo_client(encrypted, private_key) == payload


def test_sign_verify_envelope() -> None:
    issuer_public_key, issuer_private_key = generate_issuer_signing_keypair()
    envelope = {"profile_id": "prof_demo", "encrypted_payload": "abc", "issuer_public_key": issuer_public_key}
    signature = sign_envelope(envelope, issuer_private_key)
    assert verify_envelope_signature({**envelope, "signature": signature}, issuer_public_key)


def test_tampered_envelope_fails_verification() -> None:
    issuer_public_key, issuer_private_key = generate_issuer_signing_keypair()
    envelope = {"profile_id": "prof_demo", "encrypted_payload": "abc", "issuer_public_key": issuer_public_key}
    signature = sign_envelope(envelope, issuer_private_key)
    tampered = {**envelope, "encrypted_payload": "changed", "signature": signature}
    assert verify_envelope_signature(tampered, issuer_public_key) is False

