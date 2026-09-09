from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RawEvent:
    id: str
    environment_id: str
    source_type: str
    payload: dict[str, Any]
    received_at: datetime
    batch_id: str | None = None
    uploaded_by: str | None = None
    processed: bool = False


@dataclass
class IngestResult:
    batch_id: str
    accepted: int
    rejected: int
    reasons: list[str] = field(default_factory=list)
