from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.environments.domain.entities import EnvironmentStatus, EnvironmentType


class EnvironmentCreate(BaseModel):
    name: str
    type: EnvironmentType
    description: str | None = None
    authorized_sources: list[str] = []
    contact_email: str | None = None


class EnvironmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: EnvironmentType
    description: str | None
    status: EnvironmentStatus
    is_active: bool
    authorized_sources: list[str]
    created_at: datetime
