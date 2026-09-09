from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.detection.domain.entities import Severity
from app.modules.risk.application.asset_criticality import criticality_for
from app.modules.risk.domain.scoring_model import RiskResult, compute


class RiskService:
    def __init__(self, db: AsyncSession | None = None):
        self.db = db

    def score(
        self,
        *,
        severity: Severity,
        environment_type: str,
        profile: dict,
        event_count: int = 1,
        evidence: dict | None = None,
    ) -> RiskResult:
        evidence = evidence or {}
        host = evidence.get("host_name") or evidence.get("source_ip")

        return compute(
            severity=severity,
            environment_type=environment_type,
            risk_multiplier=float(profile.get("risk_multiplier", 1.0)),
            event_count=event_count,
            asset_criticality=criticality_for(host, profile.get("critical_assets", [])),
            intel_confirmed=bool(evidence.get("intel_source")),
        )
