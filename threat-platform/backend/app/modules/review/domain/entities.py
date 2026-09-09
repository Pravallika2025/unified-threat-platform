from enum import StrEnum


class DecisionAction(StrEnum):
    BLOCK_CONTAIN = "block_contain"
    MONITOR = "monitor"
    DISMISS_FALSE_POSITIVE = "dismiss_false_positive"
    ESCALATE = "escalate"
    ARCHIVE_RESOLVE = "archive_resolve"


DESTRUCTIVE_ACTIONS = {DecisionAction.BLOCK_CONTAIN}

MIN_JUSTIFICATION_LENGTH = 20
