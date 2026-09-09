"""Incident lifecycle — section 9.

The transitions are the process. Encoding them here means an incident can never
reach 'action executed' without passing through analyst review.
"""

from enum import StrEnum

from app.core.exceptions import ValidationError


class IncidentStatus(StrEnum):
    NEW = "new"
    IN_REVIEW = "in_review"
    INVESTIGATING = "investigating"
    DECIDED = "decided"
    ACTION_EXECUTED = "action_executed"
    CLOSED = "closed"
    DISMISSED = "dismissed"


ALLOWED_TRANSITIONS: dict[IncidentStatus, set[IncidentStatus]] = {
    IncidentStatus.NEW: {IncidentStatus.IN_REVIEW, IncidentStatus.DISMISSED},
    IncidentStatus.IN_REVIEW: {IncidentStatus.INVESTIGATING, IncidentStatus.DISMISSED},
    IncidentStatus.INVESTIGATING: {IncidentStatus.DECIDED, IncidentStatus.DISMISSED},
    IncidentStatus.DECIDED: {IncidentStatus.ACTION_EXECUTED, IncidentStatus.CLOSED},
    IncidentStatus.ACTION_EXECUTED: {IncidentStatus.CLOSED},
    IncidentStatus.CLOSED: set(),
    IncidentStatus.DISMISSED: set(),
}


def assert_can_transition(current: IncidentStatus, target: IncidentStatus) -> None:
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ValidationError(
            f"Cannot move an incident from '{current}' to '{target}'",
            details={"allowed": sorted(str(s) for s in allowed)},
        )


def is_terminal(status: IncidentStatus) -> bool:
    return not ALLOWED_TRANSITIONS.get(status, set())
