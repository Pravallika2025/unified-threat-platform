from pydantic import BaseModel


class RiskBreakdown(BaseModel):
    score: int
    band: str
    factors: dict[str, float]
