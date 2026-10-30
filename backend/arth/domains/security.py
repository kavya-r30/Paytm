"""Credential primitives. Nothing here logs or serializes supplied PINs."""

import hashlib
import os
import re
import secrets
from pathlib import Path

from pydantic import SecretStr


def load_signing_key(path: Path) -> SecretStr:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(secrets.token_hex(32))
    value = path.read_text(encoding="utf-8")
    if not re.fullmatch("[0-9a-f]{64}", value):
        raise ValueError("auth.invalid_signing_key_file")
    return SecretStr(value)


def hash_pin(pin: str) -> str:
    if not pin.isascii() or not pin.isdigit() or not 4 <= len(pin) <= 8:
        raise ValueError("staff.invalid_pin")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(pin.encode(), salt=salt, n=16384, r=8, p=1).hex()
    return f"scrypt${salt.hex()}${digest}"


def verify_pin(pin: str, encoded: str) -> bool:
    try:
        algorithm, salt, digest = encoded.split("$")
        if algorithm != "scrypt" or not pin.isascii() or not pin.isdigit() or not 4 <= len(pin) <= 8:
            return False
        actual = hashlib.scrypt(pin.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
        return secrets.compare_digest(actual, digest)
    except (ValueError, TypeError):
        return False
