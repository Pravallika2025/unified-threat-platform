"""The threshold rule is the workhorse of the platform — it gets the most tests."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.modules.detection.application.rule_engine import RuleEngine, parse_window
from app.modules.detection.domain.entities import DetectionRule, RuleType, Severity


@dataclass
class FakeEvent:
    id: str
    environment_id: str = "env-1"
    timestamp: datetime = None
    event_action: str | None = None
    event_outcome: str | None = None
    source_ip: str | None = None
    user_name: str | None = None
    host_name: str | None = None
    message: str | None = None
    bytes_out: int | None = None
    extra: dict = None

    def __post_init__(self):
        self.timestamp = self.timestamp or datetime.now(timezone.utc)
        self.extra = self.extra or {}


def brute_force_rule(count=5, window="5m") -> DetectionRule:
    return DetectionRule(
        id="AUTH-0001",
        title="Brute force",
        severity=Severity.HIGH,
        rule_type=RuleType.THRESHOLD,
        source_types=["all"],
        environments=["all"],
        logic={
            "type": "threshold",
            "where": [{"field": "event_action", "op": "eq", "value": "login_failed"}],
            "group_by": ["source_ip"],
            "count": count,
            "window": window,
        },
    )


def test_parse_window():
    assert parse_window("5m") == timedelta(minutes=5)
    assert parse_window("2h") == timedelta(hours=2)
    assert parse_window("30s") == timedelta(seconds=30)


def test_threshold_fires_when_exceeded():
    base = datetime.now(timezone.utc)
    events = [
        FakeEvent(
            id=f"e{i}",
            timestamp=base + timedelta(seconds=i * 10),
            event_action="login_failed",
            source_ip="203.0.113.5",
        )
        for i in range(6)
    ]
    findings = RuleEngine().evaluate(brute_force_rule(count=5), events)
    assert len(findings) == 1
    assert findings[0].entity == "203.0.113.5"
    assert findings[0].evidence["observed"] >= 5


def test_threshold_does_not_fire_below_count():
    base = datetime.now(timezone.utc)
    events = [
        FakeEvent(
            id=f"e{i}",
            timestamp=base + timedelta(seconds=i * 10),
            event_action="login_failed",
            source_ip="203.0.113.5",
        )
        for i in range(3)
    ]
    assert RuleEngine().evaluate(brute_force_rule(count=5), events) == []


def test_threshold_respects_the_window():
    """Six failures spread over an hour is not a brute force attempt."""
    base = datetime.now(timezone.utc)
    events = [
        FakeEvent(
            id=f"e{i}",
            timestamp=base + timedelta(minutes=i * 10),
            event_action="login_failed",
            source_ip="203.0.113.5",
        )
        for i in range(6)
    ]
    assert RuleEngine().evaluate(brute_force_rule(count=5, window="5m"), events) == []


def test_groups_are_independent():
    """Three failures each from two addresses must not add up to a detection."""
    base = datetime.now(timezone.utc)
    events = []
    for ip in ("203.0.113.5", "203.0.113.6"):
        events.extend(
            FakeEvent(
                id=f"{ip}-{i}",
                timestamp=base + timedelta(seconds=i * 5),
                event_action="login_failed",
                source_ip=ip,
            )
            for i in range(3)
        )
    assert RuleEngine().evaluate(brute_force_rule(count=5), events) == []


def test_non_matching_events_are_ignored():
    base = datetime.now(timezone.utc)
    events = [
        FakeEvent(
            id=f"e{i}",
            timestamp=base + timedelta(seconds=i * 5),
            event_action="login_success",
            source_ip="203.0.113.5",
        )
        for i in range(10)
    ]
    assert RuleEngine().evaluate(brute_force_rule(count=5), events) == []
