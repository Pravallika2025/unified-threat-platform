from app.modules.response.domain.action_type import ActionType
from app.modules.response.infrastructure.executors.base_executor import (
    BaseExecutor,
    ExecutionResult,
)


class MonitorExecutor(BaseExecutor):
    """Non-destructive: raises the watch level on an entity without blocking it."""

    action_types = {ActionType.MONITOR, ActionType.NOTIFY_ONLY}

    async def execute(self, *, target: str, params: dict) -> ExecutionResult:
        return ExecutionResult(
            success=True,
            message=f"{target} is now under heightened monitoring",
            details={"target": target, "watch_level": params.get("watch_level", "elevated")},
        )
