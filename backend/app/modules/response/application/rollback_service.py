"""Undo an executed response action using its rollback token and assigned executor."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.modules.incidents.application.timeline_service import TimelineService
from app.modules.response.domain.action_type import ActionStatus, ActionType
from app.modules.response.infrastructure.executors.account_disable_executor import (
    AccountDisableExecutor,
)
from app.modules.response.infrastructure.executors.base_executor import BaseExecutor
from app.modules.response.infrastructure.executors.edr_isolate_executor import (
    EdrIsolateExecutor,
)
from app.modules.response.infrastructure.executors.firewall_executor import (
    FirewallExecutor,
)
from app.modules.response.infrastructure.models import ResponseActionModel
from app.modules.response.infrastructure.repository import ResponseActionRepository

logger = logging.getLogger(__name__)


class RollbackService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ResponseActionRepository(db)
        self.timeline = TimelineService(db)
        self.executors: list[BaseExecutor] = [
            FirewallExecutor(),
            AccountDisableExecutor(),
            EdrIsolateExecutor(),
        ]

    async def rollback(self, action_id: str, *, actor_id: str) -> ResponseActionModel:
        action = await self.repo.get(action_id)
        if action is None:
            raise NotFoundError("Response action not found")

        if not action.rollback_token:
            raise ValidationError("This action does not have a valid rollback token or is not reversible")

        action_type = ActionType(action.action_type)
        executor = self._find_executor(action_type)
        if not executor:
            raise ValidationError(f"No executor available to perform rollback for action type {action_type}")

        result = await executor.rollback(rollback_token=action.rollback_token)
        if not result.success:
            raise ValidationError(f"Rollback failed: {result.message}")

        action.status = str(ActionStatus.ROLLED_BACK)
        action.result = {
            **(action.result or {}),
            "rollback": {
                "message": result.message,
                "rolled_back_by": actor_id,
                **result.details,
            },
        }
        await self.db.flush()

        await self.timeline.record(
            incident_id=action.incident_id,
            actor_id=actor_id,
            action="action_rolled_back",
            detail=f"Rolled back {action.action_type} on {action.target}",
            metadata=action.result.get("rollback", {}),
        )

        return action

    def _find_executor(self, action_type: ActionType) -> BaseExecutor | None:
        for executor in self.executors:
            if executor.supports(action_type):
                return executor
        return None
