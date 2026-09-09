from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.detection.infrastructure.repository import AlertRepository
from app.modules.incidents.application.evidence_service import EvidenceService
from app.modules.incidents.application.timeline_service import TimelineService
from app.modules.incidents.domain.state_machine import IncidentStatus, assert_can_transition
from app.modules.incidents.infrastructure.models import IncidentModel
from app.modules.incidents.infrastructure.repository import IncidentRepository
from app.modules.risk.domain.scoring_model import band_for
from app.shared.events import INCIDENT_CREATED, DomainEvent, event_bus
from app.shared.types import utcnow

logger = logging.getLogger(__name__)

# Alerts at or above this score open an incident automatically.
AUTO_INCIDENT_THRESHOLD = 50


class IncidentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IncidentRepository(db)
        self.alerts = AlertRepository(db)
        self.evidence = EvidenceService(db)
        self.timeline = TimelineService(db)

    async def create_from_alert(self, alert_id: str) -> IncidentModel:
        alert = await self.alerts.get(alert_id)
        if alert is None:
            raise NotFoundError("Alert not found")

        incident = await self.repo.add(
            IncidentModel(
                reference=await self.repo.next_reference(),
                title=alert.title,
                description=f"Opened from rule {alert.rule_id} on entity {alert.entity}",
                severity=alert.severity,
                risk_score=alert.risk_score,
                risk_band=band_for(alert.risk_score),
                environment_id=alert.environment_id,
                alert_ids=[alert.id],
                attack_technique=alert.attack_technique,
                status=str(IncidentStatus.NEW),
            )
        )

        alert.status = "incident_created"
        alert.incident_id = incident.id

        await self.evidence.attach(
            incident_id=incident.id,
            kind="event",
            content={
                "rule_id": alert.rule_id,
                "entity": alert.entity,
                "evidence": alert.evidence,
                "event_ids": alert.event_ids,
                "risk_factors": alert.risk_factors,
            },
            collected_by=None,
        )
        await self.timeline.record(
            incident_id=incident.id,
            actor_id=None,
            action="created",
            detail=f"Incident opened automatically from alert {alert.rule_id}",
        )

        await event_bus.publish(
            DomainEvent(
                INCIDENT_CREATED,
                {
                    "incident_id": incident.id,
                    "reference": incident.reference,
                    "severity": incident.severity,
                    "risk_score": incident.risk_score,
                    "environment_id": incident.environment_id,
                },
            )
        )
        logger.info("Created incident %s from alert %s", incident.reference, alert.id)
        return incident

    async def get(self, incident_id: str) -> IncidentModel:
        incident = await self.repo.get(incident_id)
        if incident is None:
            raise NotFoundError("Incident not found")
        return incident

    async def list(self, **filters) -> list[IncidentModel]:
        return await self.repo.list(**filters)

    async def transition(
        self, incident_id: str, target: IncidentStatus, *, actor_id: str, note: str = ""
    ) -> IncidentModel:
        incident = await self.get(incident_id)
        current = IncidentStatus(incident.status)
        assert_can_transition(current, target)

        incident.status = str(target)
        if target in (IncidentStatus.CLOSED, IncidentStatus.DISMISSED):
            incident.closed_at = utcnow()

        await self.timeline.record(
            incident_id=incident_id,
            actor_id=actor_id,
            action="status_change",
            detail=note or f"Status changed from {current} to {target}",
            metadata={"from": str(current), "to": str(target)},
        )
        await self.db.flush()
        return incident

    async def assign(self, incident_id: str, analyst_id: str, *, actor_id: str) -> IncidentModel:
        incident = await self.get(incident_id)
        incident.assigned_to = analyst_id
        await self.timeline.record(
            incident_id=incident_id,
            actor_id=actor_id,
            action="assigned",
            detail=f"Assigned to analyst {analyst_id}",
        )
        await self.db.flush()
        return incident

    async def auto_open_for_high_risk(self, alerts: list) -> list[IncidentModel]:
        """Called after a detection run. Below the threshold, alerts stay alerts."""
        created = []
        for alert in alerts:
            if alert.risk_score >= AUTO_INCIDENT_THRESHOLD:
                created.append(await self.create_from_alert(alert.id))
        return created
