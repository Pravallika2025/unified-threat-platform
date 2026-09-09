from pydantic import BaseModel


class NotificationOut(BaseModel):
    type: str
    event: str
    data: dict
