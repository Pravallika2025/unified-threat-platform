"""Pushes block rules to the perimeter firewall.

TODO: implement against your actual firewall API (pfSense, Palo Alto, FortiGate).
Requirements before you enable this in production:
  - credentials from a secrets manager, never from .env
  - every call must return a rollback_token so RollbackService can undo it
  - idempotent: re-blocking an already-blocked IP must succeed, not error
  - a hard allowlist of IPs that can never be blocked (your own gateways, DNS)
"""

from app.modules.response.domain.action_type import ActionType
from app.modules.response.infrastructure.executors.base_executor import (
    BaseExecutor,
    ExecutionResult,
)


class FirewallExecutor(BaseExecutor):
    action_types = {ActionType.BLOCK_IP, ActionType.BLOCK_PORT, ActionType.BLOCK_URL}

    async def execute(self, *, target: str, params: dict) -> ExecutionResult:
        raise NotImplementedError(
            "FirewallExecutor is not wired to a device. Keep DRY_RUN enabled "
            "until you have implemented and tested this against a lab firewall."
        )
