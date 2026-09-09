from dataclasses import dataclass
from datetime import datetime
from typing import Any

GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class AuditEntry:
    id: str
    actor_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    details: dict[str, Any]
    prev_hash: str
    entry_hash: str
    created_at: datetime
