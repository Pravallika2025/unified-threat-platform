import uuid
from datetime import datetime, timezone


def new_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime | None) -> datetime | None:
    """Normalise a datetime read back from the database to aware UTC.

    SQLite has no timezone type, so values written as aware come back naive and
    cannot be compared against utcnow(). Anywhere a stored timestamp is compared
    in Python rather than in SQL, run it through here first.
    """
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
