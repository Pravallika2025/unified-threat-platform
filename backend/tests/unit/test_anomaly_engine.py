from types import SimpleNamespace
import pytest

from app.modules.detection.application.anomaly_engine import AnomalyEngine
from app.modules.detection.domain.entities import Severity


def test_anomaly_engine_detects_bytes_outliers():
    engine = AnomalyEngine(bytes_outlier_threshold=1_000_000)
    events = [
        SimpleNamespace(
            id=f"evt-{i}",
            environment_id="env-1",
            user_name="jsmith",
            source_ip="192.168.1.50",
            host_name="workstation-9",
            bytes_out=500_000 if i < 9 else 15_000_000,
        )
        for i in range(10)
    ]

    findings = engine.evaluate(events)
    assert len(findings) >= 1
    f = findings[0]
    assert f.rule_id == "ANOMALY-0001"
    assert f.severity in {Severity.HIGH, Severity.CRITICAL}
    assert f.entity == "jsmith"
    assert f.evidence["max_single_transfer"] == 15_000_000


def test_anomaly_engine_detects_port_scan():
    engine = AnomalyEngine()
    events = [
        SimpleNamespace(
            id=f"evt-{i}",
            environment_id="env-1",
            source_ip="198.51.100.44",
            destination_port=1000 + i,
            bytes_out=0,
            event_action="network_connection",
        )
        for i in range(15)
    ]

    findings = engine.evaluate(events)
    assert any(f.rule_id == "ANOMALY-0002" for f in findings)
    f = next(f for f in findings if f.rule_id == "ANOMALY-0002")
    assert f.entity == "198.51.100.44"
    assert f.evidence["distinct_destination_ports"] == 15
