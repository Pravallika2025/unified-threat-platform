import logging

from app.modules.response.domain.action_type import ActionType
from app.modules.response.infrastructure.executors.base_executor import (
    BaseExecutor,
    ExecutionResult,
)

logger = logging.getLogger(__name__)


class NoopExecutor(BaseExecutor):
    """Dry-run executor. Logs what would have happened and changes nothing.

    This is the default in development so you can exercise the whole decision flow
    without touching a real firewall.
    """

    action_types = set(ActionType)

    async def execute(self, *, target: str, params: dict) -> ExecutionResult:
        logger.info("[DRY RUN] would act on target=%s params=%s", target, params)
        return ExecutionResult(
            success=True,
            message=f"Simulated only — no change was made to {target}",
            details={"dry_run": True, "target": target, "params": params},
        )
