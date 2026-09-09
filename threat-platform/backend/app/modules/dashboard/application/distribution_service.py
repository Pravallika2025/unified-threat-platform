from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.detection.infrastructure.repository import AlertRepository


class DistributionService:
    """Threat-type donut and top-source table."""

    def __init__(self, db: AsyncSession):
        self.alerts = AlertRepository(db)

    async def by_severity(self) -> list[dict]:
        counts = await self.alerts.count_by_severity()
        total = sum(counts.values()) or 1
        return [
            {"label": severity, "count": count, "percent": round(count / total * 100, 1)}
            for severity, count in sorted(counts.items(), key=lambda kv: -kv[1])
        ]

    async def by_rule(self, limit: int = 5) -> list[dict]:
        return [
            {"rule_id": rule_id, "count": count}
            for rule_id, count in await self.alerts.count_by_rule(limit)
        ]

    async def top_sources(self, limit: int = 5) -> list[dict]:
        return [
            {"entity": entity, "count": count, "severity": severity}
            for entity, count, severity in await self.alerts.top_entities(limit)
        ]
