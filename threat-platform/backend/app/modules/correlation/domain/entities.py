from dataclasses import dataclass, field

# MITRE ATT&CK tactic order — used to judge whether a sequence looks like a kill chain.
KILL_CHAIN_ORDER = [
    "TA0043",  # Reconnaissance
    "TA0001",  # Initial Access
    "TA0002",  # Execution
    "TA0003",  # Persistence
    "TA0004",  # Privilege Escalation
    "TA0005",  # Defense Evasion
    "TA0006",  # Credential Access
    "TA0007",  # Discovery
    "TA0008",  # Lateral Movement
    "TA0009",  # Collection
    "TA0010",  # Exfiltration
    "TA0040",  # Impact
]


@dataclass
class EventCluster:
    entity: str
    alert_ids: list[str] = field(default_factory=list)
    tactics: list[str] = field(default_factory=list)
    span_minutes: int = 0

    @property
    def progresses_kill_chain(self) -> bool:
        indices = [KILL_CHAIN_ORDER.index(t) for t in self.tactics if t in KILL_CHAIN_ORDER]
        return len(set(indices)) >= 2 and indices == sorted(indices)
