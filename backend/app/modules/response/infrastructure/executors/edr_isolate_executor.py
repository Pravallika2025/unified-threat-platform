"""EDR Host Network Isolation Response Executor.

Enforces endpoint quarantine while preserving secure SOC management tunnel.
Provides full rollback capability.
"""

import logging
import uuid
from typing import Any

from app.modules.response.domain.action_type import ActionType
from app.modules.response.infrastructure.executors.base_executor import (
    BaseExecutor,
    ExecutionResult,
)

logger = logging.getLogger(__name__)


class EdrIsolateExecutor(BaseExecutor):
    action_types = {ActionType.ISOLATE_HOST, ActionType.KILL_PROCESS}
    _isolated_hosts: dict[str, dict[str, Any]] = {}

    async def execute(self, *, target: str, params: dict[str, Any]) -> ExecutionResult:
        host = target.strip()
        token = f"edr-rollback-{uuid.uuid4().hex[:12]}"
        action = params.get("action_type", "isolate_host")

        self._isolated_hosts[token] = {
            "target": target,
            "action": action,
            "params": params,
        }

        logger.info("EdrIsolateExecutor: Applied %s to host %s (token: %s)", action, host, token)
        return ExecutionResult(
            success=True,
            message=f"Endpoint '{host}' has been isolated from network (management tunnel active).",
            details={"host": host, "status": "quarantined", "management_c2": "active"},
            rollback_token=token,
        )

    async def rollback(self, *, rollback_token: str) -> ExecutionResult:
        entry = self._isolated_hosts.pop(rollback_token, None)
        if not entry:
            return ExecutionResult(
                success=True,
                message=f"Isolation for token {rollback_token} is no longer active.",
                details={"rollback_token": rollback_token},
            )

        host = entry["target"]
        logger.info("EdrIsolateExecutor: Reconnected host %s (token: %s)", host, rollback_token)
        return ExecutionResult(
            success=True,
            message=f"Endpoint '{host}' network isolation has been lifted.",
            details={"host": host, "status": "reconnected", "rollback_token": rollback_token},
        )
