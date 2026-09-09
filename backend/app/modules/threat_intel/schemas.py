from pydantic import BaseModel, ConfigDict

from app.modules.threat_intel.domain.entities import IndicatorType


class IndicatorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    value: str
    type: IndicatorType
    source: str
    confidence: int
    severity: str
    description: str | None


class IndicatorCreate(BaseModel):
    value: str
    type: IndicatorType
    source: str
    confidence: int = 50
    severity: str = "medium"
    description: str | None = None
