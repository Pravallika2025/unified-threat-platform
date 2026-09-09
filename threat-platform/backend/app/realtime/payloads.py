from typing import Any

from pydantic import BaseModel


class LivePayload(BaseModel):
    type: str          # notification | heartbeat | metrics
    event: str
    data: dict[str, Any]
