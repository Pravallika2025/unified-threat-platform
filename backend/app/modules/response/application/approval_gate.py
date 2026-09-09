"""Charter principle 3: human-in-the-loop before destructive actions.

Every executor call goes through this gate. There is no second path.
"""

import logging

from app.core.exceptions import ApprovalRequiredError
from app.modules.response.domain.action_type import ActionType, is_destructive

logger = logging.getLogger(__name__)


class ApprovalGate:
    def check(
        self,
        *,
        action: ActionType,
        decision_approved_by: str | None,
        executor_id: str,
        dry_run: bool,
    ) -> None:
        if dry_run:
            return  # simulation touches nothing

        if not is_destructive(action):
            return

        if decision_approved_by is None:
            raise ApprovalRequiredError(
                f"'{action}' is a destructive action and needs approval from a second "
                "authorised user before it can execute.",
                details={"action": str(action), "required": "approved_decision"},
            )

        if decision_approved_by == executor_id:
            logger.warning(
                "User %s attempted to execute an action they approved themselves", executor_id
            )
            raise ApprovalRequiredError(
                "The approver and the executor must be different people."
            )
