import pytest

from app.core.exceptions import ValidationError
from app.modules.incidents.domain.state_machine import (
    IncidentStatus,
    assert_can_transition,
    is_terminal,
)


def test_normal_path_is_allowed():
    assert_can_transition(IncidentStatus.NEW, IncidentStatus.IN_REVIEW)
    assert_can_transition(IncidentStatus.IN_REVIEW, IncidentStatus.INVESTIGATING)
    assert_can_transition(IncidentStatus.INVESTIGATING, IncidentStatus.DECIDED)
    assert_can_transition(IncidentStatus.DECIDED, IncidentStatus.ACTION_EXECUTED)


def test_cannot_skip_review():
    """A new incident must not jump straight to an executed action."""
    with pytest.raises(ValidationError):
        assert_can_transition(IncidentStatus.NEW, IncidentStatus.ACTION_EXECUTED)


def test_closed_is_terminal():
    assert is_terminal(IncidentStatus.CLOSED)
    with pytest.raises(ValidationError):
        assert_can_transition(IncidentStatus.CLOSED, IncidentStatus.IN_REVIEW)
