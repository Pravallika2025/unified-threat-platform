from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NormalizedEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    environment_id: str
    timestamp: datetime
    source_type: str
    event_action: str | None
    event_outcome: str | None
    event_category: str | None
    source_ip: str | None
    destination_ip: str | None
    user_name: str | None
    host_name: str | None
    message: str | None
