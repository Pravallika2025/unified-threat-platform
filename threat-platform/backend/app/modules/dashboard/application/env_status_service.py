from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.detection.infrastructure.repository import AlertRepository
from app.modules.environments.application.environment_service import EnvironmentService
from app.shared.types import as_utc, utcnow

CRITICAL_ALERTS = 5
WARNING_ALERTS = 1


class EnvStatusService:
    """Derives Healthy / Warning / Critical from actual alert volume in the last hour,
    rather than a manually-set flag."""

    def __init__(self, db: AsyncSession):
        self.environments = EnvironmentService(db)
        self.alerts = AlertRepository(db)

    async def statuses(self) -> list[dict]:
        since = utcnow() - timedelta(hours=1)
        results = []

        for env in await self.environments.list():
            recent = [
                a
                for a in await self.alerts.list(environment_id=env.id, limit=200)
                if as_utc(a.created_at) >= since
            ]
            high = [a for a in recent if a.severity in ("critical", "high")]

            if len(high) >= CRITICAL_ALERTS:
                status = "critical"
            elif len(recent) >= WARNING_ALERTS:
                status = "warning"
            else:
                status = "healthy"

            results.append(
                {
                    "id": env.id,
                    "name": env.name,
                    "type": env.type,
                    "status": status,
                    "alerts_last_hour": len(recent),
                    "high_severity": len(high),
                }
            )
        return results
