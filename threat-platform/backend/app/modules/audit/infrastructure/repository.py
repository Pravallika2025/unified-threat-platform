from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.infrastructure.models import AuditEntryModel


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, entry: AuditEntryModel) -> AuditEntryModel:
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def latest(self) -> AuditEntryModel | None:
        stmt = select(AuditEntryModel).order_by(AuditEntryModel.sequence.desc()).limit(1)
        return (await self.db.execute(stmt)).scalars().first()

    async def all_ordered(self) -> list[AuditEntryModel]:
        stmt = select(AuditEntryModel).order_by(AuditEntryModel.sequence)
        return list((await self.db.execute(stmt)).scalars())

    async def list(
        self,
        *,
        actor_id: str | None = None,
        resource_type: str | None = None,
        limit: int = 100,
    ) -> list[AuditEntryModel]:
        stmt = select(AuditEntryModel).order_by(AuditEntryModel.sequence.desc()).limit(limit)
        if actor_id:
            stmt = stmt.where(AuditEntryModel.actor_id == actor_id)
        if resource_type:
            stmt = stmt.where(AuditEntryModel.resource_type == resource_type)
        return list((await self.db.execute(stmt)).scalars())

    async def count(self) -> int:
        return int((await self.db.execute(select(func.count(AuditEntryModel.id)))).scalar_one())
