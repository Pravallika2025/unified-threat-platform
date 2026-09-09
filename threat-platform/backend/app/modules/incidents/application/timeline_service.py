from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.infrastructure.models import TimelineEntryModel
from app.modules.incidents.infrastructure.repository import TimelineRepository


class TimelineService:
    def __init__(self, db: AsyncSession):
        self.repo = TimelineRepository(db)

    async def record(
        self,
        *,
        incident_id: str,
        actor_id: str | None,
        action: str,
        detail: str,
        metadata: dict | None = None,
    ) -> TimelineEntryModel:
        return await self.repo.add(
            TimelineEntryModel(
                incident_id=incident_id,
                actor_id=actor_id,
                action=action,
                detail=detail,
                entry_metadata=metadata or {},
            )
        )

    async def list(self, incident_id: str) -> list[TimelineEntryModel]:
        return await self.repo.for_incident(incident_id)
