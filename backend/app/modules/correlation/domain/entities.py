from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

TACTIC_NAMES = {
    "TA0043": "Reconnaissance",
    "TA0042": "Resource Development",
    "TA0001": "Initial Access",
    "TA0002": "Execution",
    "TA0003": "Persistence",
    "TA0004": "Privilege Escalation",
    "TA0005": "Defense Evasion",
    "TA0006": "Credential Access",
    "TA0007": "Discovery",
    "TA0008": "Lateral Movement",
    "TA0009": "Collection",
    "TA0011": "Command and Control",
    "TA0010": "Exfiltration",
    "TA0040": "Impact",
}

# Reverse lookup for tactic names to IDs
TACTIC_NAME_TO_ID = {v.lower(): k for k, v in TACTIC_NAMES.items()}

# MITRE ATT&CK tactic order — used to judge whether a sequence looks like a kill chain.
KILL_CHAIN_ORDER = [
    "TA0043",  # Reconnaissance
    "TA0042",  # Resource Development
    "TA0001",  # Initial Access
    "TA0002",  # Execution
    "TA0003",  # Persistence
    "TA0004",  # Privilege Escalation
    "TA0005",  # Defense Evasion
    "TA0006",  # Credential Access
    "TA0007",  # Discovery
    "TA0008",  # Lateral Movement
    "TA0009",  # Collection
    "TA0011",  # Command and Control
    "TA0010",  # Exfiltration
    "TA0040",  # Impact
]


def resolve_tactic_id(tactic: str | None) -> str | None:
    if not tactic:
        return None
    cleaned = tactic.strip()
    if cleaned.upper() in TACTIC_NAMES:
        return cleaned.upper()
    return TACTIC_NAME_TO_ID.get(cleaned.lower())


@dataclass
class KillChainStage:
    stage_number: int
    tactic_id: str
    tactic_name: str
    technique: str | None
    alert_id: str
    alert_title: str
    severity: str
    entity: str
    timestamp: datetime | str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class KillChainNarrative:
    entity: str
    stages: list[KillChainStage]
    unique_tactics_count: int
    is_progressive: bool
    summary: str
    recommended_action: str


@dataclass
class EventCluster:
    entity: str
    alert_ids: list[str] = field(default_factory=list)
    tactics: list[str] = field(default_factory=list)
    span_minutes: int = 0
    environment_id: str | None = None
    environments_hit: list[str] = field(default_factory=list)

    @property
    def normalized_tactic_ids(self) -> list[str]:
        ids = []
        for t in self.tactics:
            tid = resolve_tactic_id(t)
            if tid and tid in KILL_CHAIN_ORDER:
                ids.append(tid)
        return ids

    @property
    def progresses_kill_chain(self) -> bool:
        indices = [KILL_CHAIN_ORDER.index(t) for t in self.normalized_tactic_ids]
        return len(set(indices)) >= 2 and indices == sorted(indices)
