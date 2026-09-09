from pydantic import BaseModel


class KpiOut(BaseModel):
    total_events: int
    threats_detected: int
    threats_last_24h: int
    threats_trend_pct: float
    high_risk: int
    under_review: int
    blocked_contained: int
    open_incidents: int


class TimePoint(BaseModel):
    time: str
    high: int
    medium: int
    low: int


class DistributionSlice(BaseModel):
    label: str
    count: int
    percent: float


class TopSource(BaseModel):
    entity: str
    count: int
    severity: str


class EnvStatus(BaseModel):
    id: str
    name: str
    type: str
    status: str
    alerts_last_hour: int
    high_severity: int


class DashboardOut(BaseModel):
    kpis: KpiOut
    threats_over_time: list[TimePoint]
    severity_distribution: list[DistributionSlice]
    top_sources: list[TopSource]
    environment_status: list[EnvStatus]
