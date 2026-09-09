from pydantic import BaseModel, Field

from app.modules.ingestion.domain.source_type import SourceType


class IngestRequest(BaseModel):
    environment_id: str
    source_type: SourceType
    records: list[dict] = Field(min_length=1)


class IngestResponse(BaseModel):
    batch_id: str
    accepted: int
    rejected: int
    reasons: list[str] = []
