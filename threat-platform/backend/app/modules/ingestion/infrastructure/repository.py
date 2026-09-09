from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ingestion.infrastructure.models import RawEventModel


class RawEventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_many(self, events: list[RawEventModel]) -> None:
        self.db.add_all(events)
        await self.db.flush()

    async def list_unprocessed(self, limit: int = 500) -> list[RawEventModel]:
        stmt = (
            select(RawEventModel)
            .where(RawEventModel.processed.is_(False))
            .order_by(RawEventModel.received_at)
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars())

    async def mark_processed(self, ids: list[str]) -> None:
        if not ids:
            return
        stmt = select(RawEventModel).where(RawEventModel.id.in_(ids))
        for row in (await self.db.execute(stmt)).scalars():
            row.processed = True
        await self.db.flush()

    async def count(self, environment_id: str | None = None) -> int:
        stmt = select(func.count(RawEventModel.id))
        if environment_id:
            stmt = stmt.where(RawEventModel.environment_id == environment_id)
        return int((await self.db.execute(stmt)).scalar_one())
