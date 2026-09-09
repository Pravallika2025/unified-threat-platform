from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.incidents.domain.state_machine import IncidentStatus


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    reference: str
    title: str
    description: str | None
    severity: str
    risk_score: int
    risk_band: str
    status: IncidentStatus
    environment_id: str
    alert_ids: list[str]
    assigned_to: str | None
    attack_technique: str | None
    created_at: datetime
    closed_at: datetime | None


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    kind: str
    content: dict
    content_hash: str
    collected_by: str | None
    collected_at: datetime


class TimelineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_id: str | None
    action: str
    detail: str
    entry_metadata: dict
    created_at: datetime


class IncidentDetailOut(IncidentOut):
    evidence: list[EvidenceOut] = []
    timeline: list[TimelineOut] = []


class TransitionRequest(BaseModel):
    target: IncidentStatus
    note: str = ""


class AssignRequest(BaseModel):
    analyst_id: str
