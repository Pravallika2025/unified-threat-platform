from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iam.infrastructure.models import UserModel


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: str) -> UserModel | None:
        return await self.db.get(UserModel, user_id)

    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self.db.execute(
            select(UserModel).where(func.lower(UserModel.email) == email.lower())
        )
        return result.scalar_one_or_none()

    async def list(self, *, environment_id: str | None = None) -> list[UserModel]:
        stmt = select(UserModel).order_by(UserModel.created_at.desc())
        if environment_id:
            stmt = stmt.where(UserModel.environment_id == environment_id)
        return list((await self.db.execute(stmt)).scalars())

    async def add(self, user: UserModel) -> UserModel:
        self.db.add(user)
        await self.db.flush()
        return user

    async def count(self) -> int:
        return int((await self.db.execute(select(func.count(UserModel.id)))).scalar_one())
