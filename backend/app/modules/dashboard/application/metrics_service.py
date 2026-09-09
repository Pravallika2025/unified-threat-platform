from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.detection.infrastructure.repository import AlertRepository
from app.modules.incidents.domain.state_machine import IncidentStatus
from app.modules.incidents.infrastructure.repository import IncidentRepository
from app.modules.normalization.infrastructure.repository import NormalizedEventRepository
from app.modules.response.infrastructure.repository import ResponseActionRepository
from app.shared.types import utcnow

HIGH_RISK_THRESHOLD = 60


class MetricsService:
    """Powers the KPI tiles in section 8. Every number is a real query — no placeholders."""

    def __init__(self, db: AsyncSession):
        self.events = NormalizedEventRepository(db)
        self.alerts = AlertRepository(db)
        self.incidents = IncidentRepository(db)
        self.actions = ResponseActionRepository(db)

    async def kpis(self) -> dict:
        day_ago = utcnow() - timedelta(days=1)
        two_days_ago = utcnow() - timedelta(days=2)

        total_events = await self.events.count()
        threats_today = await self.alerts.count(since=day_ago)
        threats_prior = await self.alerts.count(since=two_days_ago) - threats_today

        return {
            "total_events": total_events,
            "threats_detected": await self.alerts.count(),
            "threats_last_24h": threats_today,
            "threats_trend_pct": _pct_change(threats_today, threats_prior),
            "high_risk": await self.incidents.count(min_risk=HIGH_RISK_THRESHOLD),
            "under_review": await self.incidents.count(status=str(IncidentStatus.IN_REVIEW))
            + await self.incidents.count(status=str(IncidentStatus.INVESTIGATING)),
            "blocked_contained": await self.actions.count(status="succeeded"),
            "open_incidents": await self.incidents.count(status=str(IncidentStatus.NEW)),
        }


def _pct_change(current: int, previous: int) -> float:
    if previous <= 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 1)
