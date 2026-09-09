from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from app.core.security.password import hash_password
from app.core.security.permissions import Role
from app.modules.iam.domain.rules import can_manage_user, password_meets_policy
from app.modules.iam.infrastructure.models import UserModel
from app.modules.iam.infrastructure.repository import UserRepository
from app.modules.iam.schemas import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def create(self, data: UserCreate, *, actor_role: Role) -> UserModel:
        if not can_manage_user(actor_role, data.role):
            raise PermissionDeniedError("You cannot create a user with that role")

        ok, reason = password_meets_policy(data.password)
        if not ok:
            raise ValidationError(reason)

        if await self.repo.get_by_email(data.email):
            raise ConflictError("A user with that email already exists")

        user = UserModel(
            email=data.email.lower(),
            full_name=data.full_name,
            password_hash=hash_password(data.password),
            role=str(data.role),
            environment_id=data.environment_id,
        )
        return await self.repo.add(user)

    async def get(self, user_id: str) -> UserModel:
        user = await self.repo.get(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user

    async def list(self, environment_id: str | None = None) -> list[UserModel]:
        return await self.repo.list(environment_id=environment_id)

    async def set_active(self, user_id: str, active: bool) -> UserModel:
        user = await self.get(user_id)
        user.is_active = active
        await self.db.flush()
        return user
