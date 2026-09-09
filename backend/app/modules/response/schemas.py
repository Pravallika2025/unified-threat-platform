from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.response.domain.action_type import ActionStatus, ActionType


class ActionRequest(BaseModel):
    incident_id: str
    decision_id: str | None = None
    action_type: ActionType
    target: str
    params: dict = {}
    dry_run: bool | None = None


class ActionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    decision_id: str | None
    action_type: ActionType
    target: str
    params: dict
    status: ActionStatus
    dry_run: bool
    requested_by: str
    approved_by: str | None
    executed_by: str | None
    result: dict
    rollback_token: str | None = None
    created_at: datetime
    executed_at: datetime | None
