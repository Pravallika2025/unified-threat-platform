"""Undo an executed action using its rollback token.

TODO: implement once real executors exist. Every executor that changes state must
return a rollback_token; this service looks up the executor and calls rollback().
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.modules.response.infrastructure.repository import ResponseActionRepository


class RollbackService:
    def __init__(self, db: AsyncSession):
        self.repo = ResponseActionRepository(db)

    async def rollback(self, action_id: str, *, actor_id: str):
        action = await self.repo.get(action_id)
        if action is None or not action.rollback_token:
            raise ValidationError("This action cannot be rolled back automatically")
        raise NotImplementedError("Implement alongside your first real executor")
