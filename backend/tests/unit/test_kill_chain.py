from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest

from app.modules.correlation.application.kill_chain_builder import KillChainBuilder
from app.modules.correlation.domain.entities import EventCluster


def test_kill_chain_builder_progressive_story():
    builder = KillChainBuilder()
    now = datetime.now(timezone.utc)

    alerts = [
        SimpleNamespace(
            id="alt-1",
            title="External reconnaissance sweep",
            severity="medium",
            attack_tactic="TA0043",  # Reconnaissance
            attack_technique="T1595",
            entity="203.0.113.88",
            created_at=now - timedelta(minutes=30),
            evidence={"ports": [22, 80, 443]},
        ),
        SimpleNamespace(
            id="alt-2",
            title="SSH credential brute force",
            severity="high",
            attack_tactic="TA0001",  # Initial Access
            attack_technique="T1110",
            entity="203.0.113.88",
            created_at=now - timedelta(minutes=20),
            evidence={"attempts": 15},
        ),
        SimpleNamespace(
            id="alt-3",
            title="Sudo privilege escalation",
            severity="high",
            attack_tactic="TA0004",  # Privilege Escalation
            attack_technique="T1548",
            entity="203.0.113.88",
            created_at=now - timedelta(minutes=10),
            evidence={"cmd": "sudo su"},
        ),
        SimpleNamespace(
            id="alt-4",
            title="Abnormal outbound data transfer",
            severity="critical",
            attack_tactic="TA0010",  # Exfiltration
            attack_technique="T1048",
            entity="203.0.113.88",
            created_at=now,
            evidence={"bytes": 25000000},
        ),
    ]

    narrative = builder.build_narrative(alerts, entity="203.0.113.88")
    assert narrative.is_progressive is True
    assert len(narrative.stages) == 4
    assert narrative.unique_tactics_count == 4
    assert "Reconnaissance" in narrative.summary
    assert "Exfiltration" in narrative.summary
    assert len(narrative.recommended_action) > 10


def test_event_cluster_progresses_kill_chain():
    cluster = EventCluster(
        entity="192.168.1.100",
        alert_ids=["a1", "a2", "a3"],
        tactics=["TA0001", "TA0004", "TA0010"],
        span_minutes=45,
    )
    assert cluster.progresses_kill_chain is True
