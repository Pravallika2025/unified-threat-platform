from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


SEVERITY_WEIGHT = {
    Severity.CRITICAL: 5,
    Severity.HIGH: 4,
    Severity.MEDIUM: 3,
    Severity.LOW: 2,
    Severity.INFO: 1,
}


class RuleType(StrEnum):
    THRESHOLD = "threshold"
    MATCH = "match"
    SEQUENCE = "sequence"
    ANOMALY = "anomaly"


@dataclass(frozen=True)
class DetectionRule:
    id: str
    title: str
    severity: Severity
    rule_type: RuleType
    source_types: list[str]
    environments: list[str]
    logic: dict[str, Any]
    attack: dict[str, str] = field(default_factory=dict)
    risk: dict[str, int] = field(default_factory=dict)
    response_suggestions: list[str] = field(default_factory=list)
    description: str = ""
    enabled: bool = True

    def applies_to_environment(self, environment_type: str) -> bool:
        return "all" in self.environments or environment_type in self.environments


@dataclass
class Finding:
    """What a rule produces before it becomes a stored Alert."""

    rule_id: str
    title: str
    severity: Severity
    environment_id: str
    event_ids: list[str]
    entity: str
    evidence: dict[str, Any] = field(default_factory=dict)
    attack: dict[str, str] = field(default_factory=dict)
