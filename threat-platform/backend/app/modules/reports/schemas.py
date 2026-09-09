from pydantic import BaseModel


class ReportRequest(BaseModel):
    format: str = "json"
    environment_id: str | None = None
