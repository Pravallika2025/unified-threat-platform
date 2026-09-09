import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.modules.incidents.application.incident_service import IncidentService
from app.modules.incidents.domain.state_machine import IncidentStatus
from app.modules.review.domain.entities import (
    DESTRUCTIVE_ACTIONS,
    MIN_JUSTIFICATION_LENGTH,
    DecisionAction,
)
from app.modules.review.infrastructure.models import DecisionModel
from app.modules.review.infrastructure.repository import DecisionRepository
from app.shared.events import DECISION_MADE, DomainEvent, event_bus
from app.shared.types import utcnow

logger = logging.getLogger(__name__)


class DecisionService:
    """Section 9. Every action an analyst recommends is recorded with a written rationale
    before anything is executed."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DecisionRepository(db)
        self.incidents = IncidentService(db)

    async def record(
        self, *, incident_id: str, analyst_id: str, action: DecisionAction, justification: str
    ) -> DecisionModel:
        incident = await self.incidents.get(incident_id)

        if len(justification.strip()) < MIN_JUSTIFICATION_LENGTH:
            raise ValidationError(
                f"A justification of at least {MIN_JUSTIFICATION_LENGTH} characters is "
                "required — it becomes part of the permanent audit record."
            )

        decision = await self.repo.add(
            DecisionModel(
                incident_id=incident_id,
                analyst_id=analyst_id,
                action=str(action),
                justification=justification.strip(),
                requires_approval=action in DESTRUCTIVE_ACTIONS,
            )
        )

        if IncidentStatus(incident.status) in (IncidentStatus.NEW, IncidentStatus.IN_REVIEW):
            await self.incidents.transition(
                incident_id,
                IncidentStatus.INVESTIGATING
                if IncidentStatus(incident.status) == IncidentStatus.IN_REVIEW
                else IncidentStatus.IN_REVIEW,
                actor_id=analyst_id,
                note="Analyst began review",
            )

        await event_bus.publish(
            DomainEvent(
                DECISION_MADE,
                {
                    "decision_id": decision.id,
                    "incident_id": incident_id,
                    "action": str(action),
                    "requires_approval": decision.requires_approval,
                },
            )
        )
        return decision

    async def approve(self, decision_id: str, *, approver_id: str) -> DecisionModel:
        decision = await self.repo.get(decision_id)
        if decision is None:
            raise NotFoundError("Decision not found")
        if decision.analyst_id == approver_id:
            raise ValidationError(
                "A decision cannot be approved by the analyst who made it. "
                "Destructive actions need a second pair of eyes."
            )

        decision.approved_by = approver_id
        decision.approved_at = utcnow()
        await self.db.flush()
        logger.info("Decision %s approved by %s", decision_id, approver_id)
        return decision

    async def for_incident(self, incident_id: str) -> list[DecisionModel]:
        return await self.repo.for_incident(incident_id)

    async def pending_approval(self) -> list[DecisionModel]:
        return await self.repo.pending_approval()
