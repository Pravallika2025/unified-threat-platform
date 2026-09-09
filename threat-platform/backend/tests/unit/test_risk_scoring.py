from app.modules.detection.domain.entities import Severity
from app.modules.risk.domain.scoring_model import band_for, compute


def test_higher_severity_scores_higher():
    low = compute(severity=Severity.LOW, environment_type="enterprise")
    critical = compute(severity=Severity.CRITICAL, environment_type="enterprise")
    assert critical.score > low.score


def test_environment_context_changes_the_score():
    """The same finding matters more in a hospital than on a campus network."""
    hospital = compute(severity=Severity.HIGH, environment_type="hospital")
    college = compute(severity=Severity.HIGH, environment_type="college")
    assert hospital.score > college.score


def test_score_is_capped_at_100():
    result = compute(
        severity=Severity.CRITICAL,
        environment_type="hospital",
        event_count=500,
        asset_criticality=1.4,
        intel_confirmed=True,
        risk_multiplier=2.0,
    )
    assert result.score == 100


def test_factors_are_returned_for_explainability():
    result = compute(severity=Severity.HIGH, environment_type="enterprise")
    assert "severity_base" in result.factors
    assert "environment_impact" in result.factors


def test_bands():
    assert band_for(85) == "critical"
    assert band_for(65) == "high"
    assert band_for(40) == "medium"
    assert band_for(10) == "low"
