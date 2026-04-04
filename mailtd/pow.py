"""Proof-of-Work solver for free user account creation."""

from __future__ import annotations

import hashlib
import time


def _has_leading_zero_bits(hash_bytes: bytes, bits: int) -> bool:
    remaining = bits
    for byte in hash_bytes:
        if remaining <= 0:
            return True
        if remaining >= 8:
            if byte != 0:
                return False
            remaining -= 8
        else:
            if byte >> (8 - remaining) != 0:
                return False
            return True
    return remaining <= 0


def solve_pow(address: str, difficulty: int = 15) -> dict:
    """Compute a Proof-of-Work solution for the given email address.

    Returns a dict with keys ``t`` (unix timestamp), ``n`` (nonce string),
    and ``d`` (difficulty).
    """
    timestamp = str(int(time.time()))
    nonce = 0
    while True:
        nonce_str = str(nonce)
        digest = hashlib.sha256(
            (address + timestamp + nonce_str).encode()
        ).digest()
        if _has_leading_zero_bits(digest, difficulty):
            return {"t": int(timestamp), "n": nonce_str, "d": difficulty}
        nonce += 1
