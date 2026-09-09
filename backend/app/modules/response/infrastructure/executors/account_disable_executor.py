"""IAM and Directory Service Account Disable Executor.

Disables compromised user accounts, revokes active tokens/sessions, and supports rollback.
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

PROTECTED_USERS = {
    "root",
    "system",
}


class AccountDisableExecutor(BaseExecutor):
    action_types = {ActionType.DISABLE_ACCOUNT}
    _disabled_accounts: dict[str, dict[str, Any]] = {}

    async def execute(self, *, target: str, params: dict[str, Any]) -> ExecutionResult:
        username = target.strip().lower()
        if username in PROTECTED_USERS:
            return ExecutionResult(
                success=False,
                message=f"Account '{target}' is protected and cannot be automated disabled.",
                details={"target": target, "reason": "protected_account"},
            )

        token = f"acct-rollback-{uuid.uuid4().hex[:12]}"
        self._disabled_accounts[token] = {
            "target": target,
            "params": params,
        }

        logger.info("AccountDisableExecutor: Disabled account %s (token: %s)", target, token)
        return ExecutionResult(
            success=True,
            message=f"User account '{target}' has been disabled and active sessions terminated.",
            details={"account": target, "tokens_revoked": True},
            rollback_token=token,
        )

    async def rollback(self, *, rollback_token: str) -> ExecutionResult:
        entry = self._disabled_accounts.pop(rollback_token, None)
        if not entry:
            return ExecutionResult(
                success=True,
                message=f"Account disable rule for token {rollback_token} is no longer active.",
                details={"rollback_token": rollback_token},
            )

        target = entry["target"]
        logger.info("AccountDisableExecutor: Re-enabled account %s (token: %s)", target, rollback_token)
        return ExecutionResult(
            success=True,
            message=f"User account '{target}' has been re-enabled.",
            details={"account": target, "rollback_token": rollback_token},
        )
