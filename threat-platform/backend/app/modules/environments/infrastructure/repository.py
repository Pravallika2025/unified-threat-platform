from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.environments.infrastructure.models import EnvironmentModel


class EnvironmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, env_id: str) -> EnvironmentModel | None:
        return await self.db.get(EnvironmentModel, env_id)

    async def list(self) -> list[EnvironmentModel]:
        stmt = select(EnvironmentModel).order_by(EnvironmentModel.name)
        return list((await self.db.execute(stmt)).scalars())

    async def add(self, env: EnvironmentModel) -> EnvironmentModel:
        self.db.add(env)
        await self.db.flush()
        return env
