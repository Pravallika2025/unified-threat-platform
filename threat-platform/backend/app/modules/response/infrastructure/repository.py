from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.response.infrastructure.models import ResponseActionModel


class ResponseActionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, action: ResponseActionModel) -> ResponseActionModel:
        self.db.add(action)
        await self.db.flush()
        return action

    async def get(self, action_id: str) -> ResponseActionModel | None:
        return await self.db.get(ResponseActionModel, action_id)

    async def for_incident(self, incident_id: str) -> list[ResponseActionModel]:
        stmt = (
            select(ResponseActionModel)
            .where(ResponseActionModel.incident_id == incident_id)
            .order_by(ResponseActionModel.created_at.desc())
        )
        return list((await self.db.execute(stmt)).scalars())

    async def count(self, *, status: str | None = None) -> int:
        stmt = select(func.count(ResponseActionModel.id))
        if status:
            stmt = stmt.where(ResponseActionModel.status == status)
        return int((await self.db.execute(stmt)).scalar_one())
