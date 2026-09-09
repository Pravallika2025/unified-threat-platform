from collections import defaultdict
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.detection.infrastructure.repository import AlertRepository
from app.shared.types import as_utc, utcnow


class TimeseriesService:
    """Threats-over-time chart, bucketed hourly and split by severity band."""

    def __init__(self, db: AsyncSession):
        self.alerts = AlertRepository(db)

    async def threats_over_time(self, hours: int = 24) -> list[dict]:
        since = utcnow() - timedelta(hours=hours)
        alerts = [a for a in await self.alerts.list(limit=5000) if as_utc(a.created_at) >= since]

        buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"high": 0, "medium": 0, "low": 0})
        for hour_offset in range(hours + 1):
            label = (since + timedelta(hours=hour_offset)).strftime("%H:00")
            buckets[label] = {"high": 0, "medium": 0, "low": 0}

        for alert in alerts:
            label = as_utc(alert.created_at).strftime("%H:00")
            band = _band(alert.severity)
            buckets[label][band] = buckets[label].get(band, 0) + 1

        return [{"time": label, **counts} for label, counts in buckets.items()]


def _band(severity: str) -> str:
    if severity in ("critical", "high"):
        return "high"
    if severity == "medium":
        return "medium"
    return "low"
