from pydantic import BaseModel


class ClusterOut(BaseModel):
    entity: str
    alert_ids: list[str]
    tactics: list[str]
    span_minutes: int
    progresses_kill_chain: bool
