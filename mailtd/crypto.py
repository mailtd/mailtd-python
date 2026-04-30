"""Client-side Argon2id derivation for the Mail.td password flow.

The Mail.td web frontend and backend agree on the following derivation:

    auth_key = Argon2id(password,
                        salt = SHA256(lower(trim(address))),
                        time_cost=3, memory_cost=16384 KiB,
                        parallelism=1, hash_len=32 bytes)

SDK methods that accept ``password`` derive the auth_key locally with
:func:`derive_auth_key` so the password never leaves the client process.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, Optional

from argon2.low_level import Type, hash_secret_raw


def derive_auth_key(address: str, password: str) -> str:
    """Return the 64-char hex auth_key for ``(address, password)``.

    Parameters match the Mail.td web frontend and backend exactly.
    """
    salt = hashlib.sha256(address.strip().lower().encode("utf-8")).digest()
    raw = hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=3,
        memory_cost=16384,
        parallelism=1,
        hash_len=32,
        type=Type.ID,
    )
    return raw.hex()


def _build_reset_password_body(
    account_id: str,
    *,
    password: Optional[str],
    auth_key: Optional[str],
    address: Optional[str],
) -> Dict[str, Any]:
    """Build the request body for password-reset endpoints.

    - If ``auth_key`` is given, it is sent as-is.
    - Else if ``password`` is given, the auth_key is derived locally; this
      needs the mailbox's email address. If ``account_id`` looks like an
      email it is used directly, otherwise ``address`` must be supplied.
    - The returned body never contains a ``password`` field.
    """
    if auth_key is not None:
        return {"auth_key": auth_key}
    if password is not None:
        addr = address if address else (account_id if "@" in account_id else None)
        if not addr:
            raise ValueError(
                "mailtd: address is required when account_id is a UUID and password is used"
            )
        return {"auth_key": derive_auth_key(addr, password)}
    return {}
