"""The gate is the charter's human-in-the-loop guarantee. If these tests fail,
the platform can take destructive action without sign-off."""

import pytest

from app.core.exceptions import ApprovalRequiredError
from app.modules.response.application.approval_gate import ApprovalGate
from app.modules.response.domain.action_type import ActionType

gate = ApprovalGate()


def test_destructive_action_without_approval_is_blocked():
    with pytest.raises(ApprovalRequiredError):
        gate.check(
            action=ActionType.BLOCK_IP,
            decision_approved_by=None,
            executor_id="user-1",
            dry_run=False,
        )


def test_self_approval_is_blocked():
    with pytest.raises(ApprovalRequiredError):
        gate.check(
            action=ActionType.ISOLATE_HOST,
            decision_approved_by="user-1",
            executor_id="user-1",
            dry_run=False,
        )


def test_approved_by_someone_else_passes():
    gate.check(
        action=ActionType.BLOCK_IP,
        decision_approved_by="approver-2",
        executor_id="user-1",
        dry_run=False,
    )


def test_non_destructive_action_needs_no_approval():
    gate.check(
        action=ActionType.MONITOR,
        decision_approved_by=None,
        executor_id="user-1",
        dry_run=False,
    )


def test_dry_run_always_passes():
    gate.check(
        action=ActionType.DISABLE_ACCOUNT,
        decision_approved_by=None,
        executor_id="user-1",
        dry_run=True,
    )
