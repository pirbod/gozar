from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

from nacl.exceptions import BadSignatureError, CryptoError
from nacl.public import PrivateKey, PublicKey, SealedBox
from nacl.signing import SigningKey, VerifyKey


def _b64encode(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _b64decode(value: str) -> bytes:
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except Exception as exc:
        raise ValueError("value must be valid base64") from exc


def canonical_json(data: dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_json_text(data: dict[str, Any]) -> str:
    return canonical_json(data).decode("utf-8")


def sha256_json(data: dict) -> str:
    return hashlib.sha256(canonical_json(data)).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generate_device_keypair() -> tuple[str, str]:
    private_key = PrivateKey.generate()
    return _b64encode(bytes(private_key.public_key)), _b64encode(bytes(private_key))


def generate_issuer_signing_keypair() -> tuple[str, str]:
    private_key = SigningKey.generate()
    return _b64encode(bytes(private_key.verify_key)), _b64encode(bytes(private_key))


def public_key_fingerprint(public_key: str) -> str:
    raw = _b64decode(public_key)
    if len(raw) != 32:
        raise ValueError("device public key must be 32 bytes")
    return "pkh_" + hashlib.sha256(raw).hexdigest()[:32]


def encrypt_for_device(plaintext_json: dict, device_public_key: str) -> str:
    raw_public_key = _b64decode(device_public_key)
    if len(raw_public_key) != 32:
        raise ValueError("device public key must be 32 bytes")
    sealed_box = SealedBox(PublicKey(raw_public_key))
    return _b64encode(sealed_box.encrypt(canonical_json(plaintext_json)))


def decrypt_for_device_for_demo_client(encrypted_payload: str, device_private_key: str) -> dict:
    # The demo client private key exists only for local Phase 1 demonstration.
    raw_private_key = _b64decode(device_private_key)
    if len(raw_private_key) != 32:
        raise ValueError("device private key must be 32 bytes")
    sealed_box = SealedBox(PrivateKey(raw_private_key))
    try:
        plaintext = sealed_box.decrypt(_b64decode(encrypted_payload))
    except CryptoError as exc:
        raise ValueError("encrypted payload could not be decrypted by this demo device key") from exc
    parsed = json.loads(plaintext.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("decrypted payload must be a JSON object")
    return parsed


def sign_envelope(envelope_without_signature: dict, issuer_private_key: str) -> str:
    raw_private_key = _b64decode(issuer_private_key)
    if len(raw_private_key) != 32:
        raise ValueError("issuer signing key must be 32 bytes")
    signing_key = SigningKey(raw_private_key)
    signed = signing_key.sign(canonical_json(_without_signature(envelope_without_signature)))
    return _b64encode(signed.signature)


def verify_envelope_signature(envelope: dict, issuer_public_key: str) -> bool:
    signature = envelope.get("signature")
    if not isinstance(signature, str):
        return False
    raw_public_key = _b64decode(issuer_public_key)
    if len(raw_public_key) != 32:
        raise ValueError("issuer public key must be 32 bytes")
    verify_key = VerifyKey(raw_public_key)
    try:
        verify_key.verify(canonical_json(_without_signature(envelope)), _b64decode(signature))
    except (BadSignatureError, ValueError):
        return False
    return True


def _without_signature(envelope: dict) -> dict:
    return {key: value for key, value in envelope.items() if key != "signature"}
