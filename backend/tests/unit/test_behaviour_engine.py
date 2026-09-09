from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest

from app.modules.detection.application.behaviour_engine import BehaviourEngine
from app.modules.detection.domain.entities import Severity


def test_behaviour_engine_auth_to_priv_escalation():
    engine = BehaviourEngine()
    now = datetime.now(timezone.utc)
    events = [
        SimpleNamespace(
            id="evt-1",
            environment_id="env-1",
            user_name="contractor_1",
            event_action="login_success",
            event_outcome="success",
            event_category="authentication",
            timestamp=now - timedelta(minutes=5),
        ),
        SimpleNamespace(
            id="evt-2",
            environment_id="env-1",
            user_name="contractor_1",
            event_action="sudo_command_execution",
            event_outcome="success",
            event_category="privilege_escalation",
            timestamp=now - timedelta(minutes=2),
        ),
    ]

    findings = engine.evaluate(events)
    assert any(f.rule_id == "BEHAV-0001" for f in findings)
    f = next(f for f in findings if f.rule_id == "BEHAV-0001")
    assert f.entity == "contractor_1"
    assert "evt-1" in f.event_ids
    assert "evt-2" in f.event_ids


def test_behaviour_engine_multi_ip_access():
    engine = BehaviourEngine()
    now = datetime.now(timezone.utc)
    events = [
        SimpleNamespace(
            id=f"evt-{i}",
            environment_id="env-1",
            user_name="alice",
            source_ip=f"10.0.{i}.15",
            event_action="login_attempt",
            event_outcome="success",
            event_category="authentication",
            timestamp=now - timedelta(minutes=10 - i),
        )
        for i in range(4)
    ]

    findings = engine.evaluate(events)
    assert any(f.rule_id == "BEHAV-0003" for f in findings)
    f = next(f for f in findings if f.rule_id == "BEHAV-0003")
    assert f.entity == "alice"
    assert len(f.evidence["distinct_source_ips"]) >= 3
