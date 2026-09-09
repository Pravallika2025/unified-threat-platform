from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.infrastructure.models import (
    EvidenceModel,
    IncidentModel,
    TimelineEntryModel,
)


class IncidentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, incident: IncidentModel) -> IncidentModel:
        self.db.add(incident)
        await self.db.flush()
        return incident

    async def get(self, incident_id: str) -> IncidentModel | None:
        return await self.db.get(IncidentModel, incident_id)

    async def list(
        self,
        *,
        status: str | None = None,
        environment_id: str | None = None,
        assigned_to: str | None = None,
        limit: int = 100,
    ) -> list[IncidentModel]:
        stmt = select(IncidentModel).order_by(IncidentModel.created_at.desc()).limit(limit)
        if status:
            stmt = stmt.where(IncidentModel.status == status)
        if environment_id:
            stmt = stmt.where(IncidentModel.environment_id == environment_id)
        if assigned_to:
            stmt = stmt.where(IncidentModel.assigned_to == assigned_to)
        return list((await self.db.execute(stmt)).scalars())

    async def count(self, *, status: str | None = None, min_risk: int | None = None) -> int:
        stmt = select(func.count(IncidentModel.id))
        if status:
            stmt = stmt.where(IncidentModel.status == status)
        if min_risk is not None:
            stmt = stmt.where(IncidentModel.risk_score >= min_risk)
        return int((await self.db.execute(stmt)).scalar_one())

    async def next_reference(self) -> str:
        total = int((await self.db.execute(select(func.count(IncidentModel.id)))).scalar_one())
        return f"INC-{total + 1:06d}"


class EvidenceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, evidence: EvidenceModel) -> EvidenceModel:
        self.db.add(evidence)
        await self.db.flush()
        return evidence

    async def for_incident(self, incident_id: str) -> list[EvidenceModel]:
        stmt = (
            select(EvidenceModel)
            .where(EvidenceModel.incident_id == incident_id)
            .order_by(EvidenceModel.collected_at)
        )
        return list((await self.db.execute(stmt)).scalars())


class TimelineRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, entry: TimelineEntryModel) -> TimelineEntryModel:
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def for_incident(self, incident_id: str) -> list[TimelineEntryModel]:
        stmt = (
            select(TimelineEntryModel)
            .where(TimelineEntryModel.incident_id == incident_id)
            .order_by(TimelineEntryModel.created_at)
        )
        return list((await self.db.execute(stmt)).scalars())
