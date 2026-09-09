import hashlib
import json
from typing import Any


def sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def canonical_json(payload: Any) -> str:
    """Stable serialisation so hashes are reproducible across runs."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def canonical_timestamp(value) -> str:
    """Timestamps must hash identically before and after a database round trip.

    SQLite does not preserve tzinfo, so a naive value read back from storage would
    otherwise produce a different hash than the aware value that was written.
    Everything is normalised to naive UTC microseconds.
    """
    from datetime import datetime, timezone

    if not isinstance(value, datetime):
        return str(value)
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value.isoformat(timespec="microseconds")
