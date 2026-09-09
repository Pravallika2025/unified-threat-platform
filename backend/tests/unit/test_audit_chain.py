from datetime import datetime, timezone

from app.modules.audit.application.audit_service import compute_entry_hash
from app.modules.audit.domain.entities import GENESIS_HASH


def entry_hash(prev: str, details: dict, action: str = "test.action") -> str:
    return compute_entry_hash(
        prev_hash=prev,
        actor_id="user-1",
        action=action,
        resource_type="incident",
        resource_id="inc-1",
        details=details,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def test_hash_is_deterministic():
    assert entry_hash(GENESIS_HASH, {"a": 1}) == entry_hash(GENESIS_HASH, {"a": 1})


def test_changing_details_changes_the_hash():
    assert entry_hash(GENESIS_HASH, {"a": 1}) != entry_hash(GENESIS_HASH, {"a": 2})


def test_changing_the_predecessor_changes_the_hash():
    """This is the property that makes the chain tamper-evident: editing any earlier
    entry invalidates every hash after it."""
    first = entry_hash(GENESIS_HASH, {"a": 1})
    tampered = entry_hash(GENESIS_HASH, {"a": 999})
    assert entry_hash(first, {"b": 2}) != entry_hash(tampered, {"b": 2})


def test_key_order_does_not_matter():
    """Canonical JSON means dict ordering cannot produce a false mismatch."""
    assert entry_hash(GENESIS_HASH, {"a": 1, "b": 2}) == entry_hash(
        GENESIS_HASH, {"b": 2, "a": 1}
    )
