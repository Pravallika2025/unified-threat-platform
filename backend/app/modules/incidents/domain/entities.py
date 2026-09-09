from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Evidence:
    id: str
    incident_id: str
    kind: str            # event | note | artifact | intel
    content: dict[str, Any]
    content_hash: str
    collected_by: str | None
    collected_at: datetime


@dataclass
class TimelineEntry:
    id: str
    incident_id: str
    actor_id: str | None
    action: str
    detail: str
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
