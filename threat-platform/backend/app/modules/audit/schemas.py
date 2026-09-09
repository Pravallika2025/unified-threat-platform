from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sequence: int
    actor_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    details: dict
    entry_hash: str
    created_at: datetime


class ChainVerification(BaseModel):
    valid: bool
    checked: int
    broken_at: str | None
    reason: str | None
