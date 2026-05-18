from __future__ import annotations

import base64
import hashlib
import json
import secrets
from itertools import cycle

try:
    from nacl.encoding import Base64Encoder
    from nacl.public import PrivateKey, PublicKey, SealedBox

    _HAS_NACL = True
except Exception:
    _HAS_NACL = False

_NACL_PREFIX = "demo-nacl:v1:"
_FALLBACK_PREFIX = "demo-fallback:v1:"


def generate_demo_keypair() -> tuple[str, str]:
    if _HAS_NACL:
        private_key = PrivateKey.generate()
        public_key = private_key.public_key
        return (
            f"{_NACL_PREFIX}{public_key.encode(encoder=Base64Encoder).decode()}",
            f"{_NACL_PREFIX}{private_key.encode(encoder=Base64Encoder).decode()}",
        )

    token = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    return (f"{_FALLBACK_PREFIX}{token}", f"{_FALLBACK_PREFIX}{token}")


def encrypt_demo_envelope(plaintext: str, recipient_public_key: str) -> str:
    if recipient_public_key.startswith(_NACL_PREFIX) and _HAS_NACL:
        key = PublicKey(recipient_public_key.removeprefix(_NACL_PREFIX), encoder=Base64Encoder)
        ciphertext = SealedBox(key).encrypt(plaintext.encode("utf-8"))
        return f"{_NACL_PREFIX}{base64.b64encode(ciphertext).decode()}"

    nonce = secrets.token_hex(12)
    stream = _fallback_stream(recipient_public_key, nonce)
    ciphertext = bytes(byte ^ key for byte, key in zip(plaintext.encode("utf-8"), cycle(stream)))
    payload = {
        "algorithm": "deterministic-demo-fallback-not-production",
        "nonce": nonce,
        "ciphertext": base64.b64encode(ciphertext).decode(),
    }
    encoded = base64.urlsafe_b64encode(json.dumps(payload, sort_keys=True).encode()).decode()
    return f"{_FALLBACK_PREFIX}{encoded}"


def decrypt_demo_envelope_for_tests_only(ciphertext: str, private_key: str) -> str:
    if ciphertext.startswith(_NACL_PREFIX) and private_key.startswith(_NACL_PREFIX) and _HAS_NACL:
        key = PrivateKey(private_key.removeprefix(_NACL_PREFIX), encoder=Base64Encoder)
        raw = base64.b64decode(ciphertext.removeprefix(_NACL_PREFIX))
        return SealedBox(key).decrypt(raw).decode("utf-8")

    encoded = ciphertext.removeprefix(_FALLBACK_PREFIX)
    payload = json.loads(base64.urlsafe_b64decode(encoded.encode()).decode())
    nonce = str(payload["nonce"])
    stream = _fallback_stream(private_key, nonce)
    raw = base64.b64decode(str(payload["ciphertext"]))
    plaintext = bytes(byte ^ key for byte, key in zip(raw, cycle(stream)))
    return plaintext.decode("utf-8")


def hash_envelope(ciphertext: str) -> str:
    return f"sha256:{hashlib.sha256(ciphertext.encode('utf-8')).hexdigest()}"


def _fallback_stream(key_material: str, nonce: str) -> bytes:
    return hashlib.sha256(f"{key_material}:{nonce}".encode()).digest()
