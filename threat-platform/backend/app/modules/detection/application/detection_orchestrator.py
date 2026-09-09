"""Stage 3: runs every engine over a window of normalized events, de-duplicates
findings, scores them, and persists alerts.
"""

import logging
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.detection.application.anomaly_engine import AnomalyEngine
from app.modules.detection.application.behaviour_engine import BehaviourEngine
from app.modules.detection.application.rule_engine import RuleEngine
from app.modules.detection.application.rule_loader import rule_loader
from app.modules.detection.application.signature_engine import SignatureEngine
from app.modules.detection.domain.entities import Finding
from app.modules.detection.infrastructure.models import AlertModel
from app.modules.detection.infrastructure.repository import AlertRepository
from app.modules.environments.application.environment_service import EnvironmentService
from app.modules.environments.application.profile_service import load_profile
from app.modules.normalization.infrastructure.repository import NormalizedEventRepository
from app.modules.risk.application.risk_service import RiskService
from app.modules.threat_intel.application.ioc_matcher import build_ioc_index
from app.shared.events import ALERT_RAISED, DomainEvent, event_bus
from app.shared.types import utcnow

logger = logging.getLogger(__name__)


class DetectionOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.events = NormalizedEventRepository(db)
        self.alerts = AlertRepository(db)
        self.environments = EnvironmentService(db)
        self.risk = RiskService(db)
        self.rule_engine = RuleEngine()
        self.anomaly_engine = AnomalyEngine()
        self.behaviour_engine = BehaviourEngine()

    async def run(self, *, environment_id: str, lookback_minutes: int = 60) -> list[AlertModel]:
        env = await self.environments.get(environment_id)
        profile = load_profile(env.type)

        since = utcnow() - timedelta(minutes=lookback_minutes)
        events = await self.events.in_window(environment_id=environment_id, since=since)
        if not events:
            logger.info("No events to analyse for environment %s", env.name)
            return []

        findings: list[Finding] = []

        # 1. YAML rules
        for rule in rule_loader.load_all():
            if not rule.applies_to_environment(env.type):
                continue
            scoped = [
                e for e in events
                if "all" in rule.source_types or e.source_type in rule.source_types
            ]
            findings.extend(self.rule_engine.evaluate(rule, scoped))

        # 2. Signatures / IOCs
        signature_engine = SignatureEngine(await build_ioc_index(self.db))
        findings.extend(signature_engine.evaluate(events))

        # 3. Anomaly + behaviour (stubs today)
        findings.extend(self.anomaly_engine.evaluate(events))
        findings.extend(self.behaviour_engine.evaluate(events))

        return await self._persist(findings, profile=profile, environment_type=env.type)

    async def _persist(
        self, findings: list[Finding], *, profile: dict, environment_type: str
    ) -> list[AlertModel]:
        created: list[AlertModel] = []

        for finding in findings:
            # Suppress a repeat of the same rule + entity inside the dedup window.
            if await self.alerts.exists_recent(
                rule_id=finding.rule_id, entity=finding.entity, minutes=15
            ):
                continue

            risk = self.risk.score(
                severity=finding.severity,
                environment_type=environment_type,
                profile=profile,
                event_count=len(finding.event_ids),
                evidence=finding.evidence,
            )

            alert = AlertModel(
                rule_id=finding.rule_id,
                title=finding.title,
                severity=str(finding.severity),
                environment_id=finding.environment_id,
                entity=finding.entity,
                event_ids=finding.event_ids,
                evidence=finding.evidence,
                attack_tactic=finding.attack.get("tactic"),
                attack_technique=finding.attack.get("technique"),
                risk_score=risk.score,
                risk_factors=risk.factors,
            )
            created.append(await self.alerts.add(alert))

            await event_bus.publish(
                DomainEvent(
                    ALERT_RAISED,
                    {
                        "alert_id": alert.id,
                        "title": alert.title,
                        "severity": alert.severity,
                        "risk_score": alert.risk_score,
                        "environment_id": alert.environment_id,
                    },
                )
            )

        logger.info("Detection produced %d new alerts", len(created))
        return created
