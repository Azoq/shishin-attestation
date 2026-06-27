#!/usr/bin/env python3
"""Independently verify a Shishin attestation day.

Usage:
    python verify.py YYYY-MM-DD

Reads reveals/<date>.json (the revealed payload) and chain/<date>.json (the
commitment Shishin published and timestamped on the day), recomputes the
chained hash, and checks that they match. Standard library only, so anyone
can audit the record without trusting Shishin or installing anything.

To also verify the timestamp, install the OpenTimestamps client and run:
    ots verify chain/<date>.json.ots
"""
import hashlib
import json
import sys
from pathlib import Path

# Genesis prev_hash for the first day. Documented in README.md so anyone can
# recompute it: SHA256("shishin-attestation/v1").
GENESIS_PREIMAGE = b"shishin-attestation/v1"
GENESIS = hashlib.sha256(GENESIS_PREIMAGE).hexdigest()

ROOT = Path(__file__).resolve().parent


def canonical(payload: dict) -> bytes:
    """Deterministic serialization: compact JSON, sorted keys, UTF-8.

    Every number in the payload is stored as a string, so this serialization
    is byte-for-byte reproducible in any language (no float-formatting drift).
    """
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def chain_hash(payload: dict, prev_hash: str) -> str:
    """H[t] = SHA256( canonical(payload) || '|' || H[t-1] )."""
    return hashlib.sha256(
        canonical(payload) + b"|" + prev_hash.encode("ascii")
    ).hexdigest()


def verify_day(date: str) -> bool:
    commit = json.loads((ROOT / "chain" / f"{date}.json").read_text("utf-8"))
    reveal = json.loads((ROOT / "reveals" / f"{date}.json").read_text("utf-8"))
    payload = reveal["payload"]
    prev_hash = commit["prev_hash"]
    recomputed = chain_hash(payload, prev_hash)
    ok = recomputed == commit["commit_hash"]
    print(f"date         {date}")
    print(f"prev_hash    {prev_hash}")
    print(f"commit_hash  {commit['commit_hash']}")
    print(f"recomputed   {recomputed}")
    print(
        "RESULT       "
        + ("OK - payload matches the timestamped commitment"
           if ok else "MISMATCH - the record was altered")
    )
    return ok


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        print(f"genesis = {GENESIS}")
        sys.exit(2)
    sys.exit(0 if verify_day(sys.argv[1]) else 1)
