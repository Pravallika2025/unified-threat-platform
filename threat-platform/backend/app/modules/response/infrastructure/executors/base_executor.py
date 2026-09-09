from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.modules.response.domain.action_type import ActionType


@dataclass
class ExecutionResult:
    success: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    rollback_token: str | None = None


class BaseExecutor(ABC):
    """One executor per enforcement point. Must be idempotent — the same action
    applied twice should not produce a different end state."""

    action_types: set[ActionType] = set()

    def supports(self, action: ActionType) -> bool:
        return action in self.action_types

    @abstractmethod
    async def execute(self, *, target: str, params: dict[str, Any]) -> ExecutionResult: ...

    async def rollback(self, *, rollback_token: str) -> ExecutionResult:
        return ExecutionResult(False, "Rollback is not supported by this executor")
