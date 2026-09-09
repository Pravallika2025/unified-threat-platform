from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.environments.infrastructure.models import EnvironmentModel
from app.modules.environments.infrastructure.repository import EnvironmentRepository
from app.modules.environments.schemas import EnvironmentCreate


class EnvironmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EnvironmentRepository(db)

    async def create(self, data: EnvironmentCreate) -> EnvironmentModel:
        env = EnvironmentModel(
            name=data.name,
            type=str(data.type),
            description=data.description,
            authorized_sources=data.authorized_sources,
            contact_email=data.contact_email,
        )
        return await self.repo.add(env)

    async def get(self, env_id: str) -> EnvironmentModel:
        env = await self.repo.get(env_id)
        if env is None:
            raise NotFoundError("Environment not found")
        return env

    async def list(self) -> list[EnvironmentModel]:
        return await self.repo.list()

    async def set_status(self, env_id: str, status: str) -> EnvironmentModel:
        env = await self.get(env_id)
        env.status = status
        await self.db.flush()
        return env
