from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.review.domain.entities import DecisionAction


class DecisionCreate(BaseModel):
    incident_id: str
    action: DecisionAction
    justification: str


class DecisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    analyst_id: str
    action: DecisionAction
    justification: str
    requires_approval: bool
    approved_by: str | None
    approved_at: datetime | None
    created_at: datetime
