from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.application.incident_service import IncidentService
from app.modules.incidents.domain.state_machine import IncidentStatus


class ReviewQueueService:
    """The analyst work queue — highest risk first, oldest first as a tiebreak."""

    def __init__(self, db: AsyncSession):
        self.incidents = IncidentService(db)

    async def queue(self, *, assigned_to: str | None = None, limit: int = 50) -> list:
        pending = []
        for status in (IncidentStatus.NEW, IncidentStatus.IN_REVIEW, IncidentStatus.INVESTIGATING):
            pending.extend(
                await self.incidents.list(
                    status=str(status), assigned_to=assigned_to, limit=limit
                )
            )
        pending.sort(key=lambda i: (-i.risk_score, i.created_at))
        return pending[:limit]
