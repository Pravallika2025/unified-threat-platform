"""Transparent risk scoring — section 5.

An analyst must be able to read a score and see exactly why it landed there,
so every contributing factor is returned alongside the number.
"""

from dataclasses import dataclass, field

from app.modules.detection.domain.entities import SEVERITY_WEIGHT, Severity

# Section 2 environments carry different blast radius for the same technique.
ENVIRONMENT_IMPACT = {
    "hospital": 1.35,
    "government": 1.30,
    "airport": 1.30,
    "enterprise": 1.15,
    "college": 1.00,
    "school": 1.00,
    "custom": 1.00,
}

MAX_SCORE = 100


@dataclass
class RiskResult:
    score: int
    band: str
    factors: dict[str, float] = field(default_factory=dict)


def band_for(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def compute(
    *,
    severity: Severity,
    environment_type: str,
    risk_multiplier: float = 1.0,
    event_count: int = 1,
    asset_criticality: float = 1.0,
    intel_confirmed: bool = False,
) -> RiskResult:
    base = SEVERITY_WEIGHT.get(severity, 1) * 12          # 12 - 60
    env_factor = ENVIRONMENT_IMPACT.get(environment_type, 1.0)
    volume_factor = min(1.0 + (event_count - 1) * 0.03, 1.5)
    intel_factor = 1.25 if intel_confirmed else 1.0

    raw = base * env_factor * volume_factor * asset_criticality * intel_factor * risk_multiplier
    score = max(1, min(MAX_SCORE, round(raw)))

    return RiskResult(
        score=score,
        band=band_for(score),
        factors={
            "severity_base": base,
            "environment_impact": round(env_factor, 2),
            "event_volume": round(volume_factor, 2),
            "asset_criticality": round(asset_criticality, 2),
            "threat_intel": round(intel_factor, 2),
            "profile_multiplier": round(risk_multiplier, 2),
        },
    )
