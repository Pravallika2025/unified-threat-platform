from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.normalization.infrastructure.models import NormalizedEventModel


class NormalizedEventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_many(self, events: list[NormalizedEventModel]) -> None:
        self.db.add_all(events)
        await self.db.flush()

    async def in_window(
        self, *, environment_id: str, since: datetime, until: datetime | None = None
    ) -> list[NormalizedEventModel]:
        stmt = select(NormalizedEventModel).where(
            NormalizedEventModel.environment_id == environment_id,
            NormalizedEventModel.timestamp >= since,
        )
        if until:
            stmt = stmt.where(NormalizedEventModel.timestamp <= until)
        return list((await self.db.execute(stmt.order_by(NormalizedEventModel.timestamp))).scalars())

    async def by_ids(self, ids: list[str]) -> list[NormalizedEventModel]:
        if not ids:
            return []
        stmt = select(NormalizedEventModel).where(NormalizedEventModel.id.in_(ids))
        return list((await self.db.execute(stmt)).scalars())

    async def count(self, environment_id: str | None = None) -> int:
        stmt = select(func.count(NormalizedEventModel.id))
        if environment_id:
            stmt = stmt.where(NormalizedEventModel.environment_id == environment_id)
        return int((await self.db.execute(stmt)).scalar_one())

    async def recent(self, limit: int = 50) -> list[NormalizedEventModel]:
        stmt = select(NormalizedEventModel).order_by(
            NormalizedEventModel.timestamp.desc()
        ).limit(limit)
        return list((await self.db.execute(stmt)).scalars())
