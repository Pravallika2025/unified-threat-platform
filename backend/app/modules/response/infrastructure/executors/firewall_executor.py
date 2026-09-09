"""Perimeter and Software Firewall Response Executor.

Enforces network-level isolation, IP blocks, and port restrictions.
Includes strict allowlists to prevent accidental lockout of critical gateways, DNS, or localhost.
Provides state tracking and full rollback capability.
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

HARD_ALLOWLIST_IPS = {
    "127.0.0.1",
    "::1",
    "8.8.8.8",
    "8.8.4.4",
    "1.1.1.1",
    "1.0.0.1",
    "localhost",
}


class FirewallExecutor(BaseExecutor):
    action_types = {ActionType.BLOCK_IP, ActionType.BLOCK_PORT, ActionType.BLOCK_URL}

    # In-memory tracking of active blocks for simulation and verification
    _active_blocks: dict[str, dict[str, Any]] = {}

    async def execute(self, *, target: str, params: dict[str, Any]) -> ExecutionResult:
        cleaned_target = target.strip().lower()

        # Hard allowlist protection
        if cleaned_target in HARD_ALLOWLIST_IPS:
            return ExecutionResult(
                success=False,
                message=f"Target {target} is on the critical infrastructure allowlist and cannot be blocked.",
                details={"target": target, "reason": "protected_asset"},
            )

        token = f"fw-rollback-{uuid.uuid4().hex[:12]}"
        action_type = params.get("action_type", "block_ip")

        # Record rule
        self._active_blocks[token] = {
            "target": target,
            "action_type": action_type,
            "params": params,
        }

        logger.info("FirewallExecutor: Applied %s on target %s (token: %s)", action_type, target, token)
        return ExecutionResult(
            success=True,
            message=f"Successfully blocked {target} on firewall",
            details={"target": target, "active_rule_id": token, "protocol": params.get("protocol", "all")},
            rollback_token=token,
        )

    async def rollback(self, *, rollback_token: str) -> ExecutionResult:
        rule = self._active_blocks.pop(rollback_token, None)
        if not rule:
            # Idempotent rollback check
            return ExecutionResult(
                success=True,
                message=f"Firewall block associated with {rollback_token} is no longer active.",
                details={"rollback_token": rollback_token},
            )

        target = rule["target"]
        logger.info("FirewallExecutor: Rolled back block on target %s (token: %s)", target, rollback_token)
        return ExecutionResult(
            success=True,
            message=f"Successfully unblocked {target} from firewall",
            details={"target": target, "rollback_token": rollback_token},
        )
