"""Authenticated encryption for NeuroShield's persistent video-analysis cache."""
import base64
import binascii
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ENV_NAME = "NEUROSHIELD_CACHE_KEY"
FORMAT = "neuroshield-aes256gcm-v1"


def _key():
    encoded = os.environ.get(ENV_NAME)
    if not encoded:
        raise RuntimeError(f"{ENV_NAME} is required to use the encrypted analysis cache")
    try:
        key = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise RuntimeError(f"{ENV_NAME} must be a base64-encoded 32-byte key") from exc
    if len(key) != 32:
        raise RuntimeError(f"{ENV_NAME} must decode to exactly 32 bytes")
    return key


def validate_cache_key():
    _key()


def encrypt_result(video_id, result):
    nonce = os.urandom(12)
    plaintext = json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ciphertext = AESGCM(_key()).encrypt(nonce, plaintext, video_id.encode("ascii"))
    return {
        "format": FORMAT,
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
    }


def decrypt_result(video_id, envelope):
    if not isinstance(envelope, dict) or envelope.get("format") != FORMAT:
        raise ValueError("Unsupported encrypted cache format")
    nonce = base64.b64decode(envelope["nonce"], validate=True)
    ciphertext = base64.b64decode(envelope["ciphertext"], validate=True)
    if len(nonce) != 12:
        raise ValueError("Invalid encrypted cache nonce")
    plaintext = AESGCM(_key()).decrypt(nonce, ciphertext, video_id.encode("ascii"))
    return json.loads(plaintext.decode("utf-8"))
