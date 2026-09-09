from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    rule_id: str
    title: str
    severity: str
    environment_id: str
    entity: str
    event_ids: list[str]
    evidence: dict
    attack_tactic: str | None
    attack_technique: str | None
    risk_score: int
    risk_factors: dict
    status: str
    incident_id: str | None
    created_at: datetime


class RunDetectionRequest(BaseModel):
    environment_id: str
    lookback_minutes: int = 60
