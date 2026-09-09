import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.modules.incidents.application.incident_service import IncidentService
from app.modules.incidents.application.timeline_service import TimelineService
from app.modules.incidents.domain.state_machine import IncidentStatus
from app.modules.response.application.approval_gate import ApprovalGate
from app.modules.response.domain.action_type import ActionStatus, ActionType, is_destructive
from app.modules.response.infrastructure.executors.account_disable_executor import (
    AccountDisableExecutor,
)
from app.modules.response.infrastructure.executors.base_executor import BaseExecutor
from app.modules.response.infrastructure.executors.edr_isolate_executor import (
    EdrIsolateExecutor,
)
from app.modules.response.infrastructure.executors.firewall_executor import (
    FirewallExecutor,
)
from app.modules.response.infrastructure.executors.monitor_executor import MonitorExecutor
from app.modules.response.infrastructure.executors.noop_executor import NoopExecutor
from app.modules.response.infrastructure.models import ResponseActionModel
from app.modules.response.infrastructure.repository import ResponseActionRepository
from app.modules.review.infrastructure.repository import DecisionRepository
from app.shared.events import ACTION_EXECUTED, DomainEvent, event_bus
from app.shared.types import utcnow

logger = logging.getLogger(__name__)


class ResponseOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ResponseActionRepository(db)
        self.decisions = DecisionRepository(db)
        self.incidents = IncidentService(db)
        self.timeline = TimelineService(db)
        self.gate = ApprovalGate()

        # Real executors first, NoopExecutor last as the catch-all fallback.
        self.executors: list[BaseExecutor] = [
            FirewallExecutor(),
            AccountDisableExecutor(),
            EdrIsolateExecutor(),
            MonitorExecutor(),
            NoopExecutor(),
        ]

    async def request(
        self,
        *,
        incident_id: str,
        decision_id: str | None,
        action_type: ActionType,
        target: str,
        params: dict,
        requested_by: str,
        dry_run: bool | None = None,
    ) -> ResponseActionModel:
        await self.incidents.get(incident_id)  # 404s if the incident does not exist

        if not target.strip():
            raise ValidationError("A response action needs a target")

        effective_dry_run = settings.is_dev if dry_run is None else dry_run

        action = await self.repo.add(
            ResponseActionModel(
                incident_id=incident_id,
                decision_id=decision_id,
                action_type=str(action_type),
                target=target,
                params=params,
                requested_by=requested_by,
                dry_run=effective_dry_run,
                status=str(
                    ActionStatus.PENDING_APPROVAL
                    if is_destructive(action_type) and not effective_dry_run
                    else ActionStatus.APPROVED
                ),
            )
        )
        await self.timeline.record(
            incident_id=incident_id,
            actor_id=requested_by,
            action="action_requested",
            detail=f"Requested {action_type} on {target}",
            metadata={"dry_run": effective_dry_run},
        )
        return action

    async def execute(self, action_id: str, *, executor_id: str) -> ResponseActionModel:
        action = await self.repo.get(action_id)
        if action is None:
            raise NotFoundError("Response action not found")

        action_type = ActionType(action.action_type)
        approved_by = None
        if action.decision_id:
            decision = await self.decisions.get(action.decision_id)
            approved_by = decision.approved_by if decision else None

        # THE GATE. Do not add a path around this.
        self.gate.check(
            action=action_type,
            decision_approved_by=approved_by,
            executor_id=executor_id,
            dry_run=action.dry_run,
        )

        executor = self._executor_for(action_type, dry_run=action.dry_run)
        action.status = str(ActionStatus.EXECUTING)
        await self.db.flush()

        try:
            result = await executor.execute(target=action.target, params=action.params)
            action.status = str(
                ActionStatus.SUCCEEDED if result.success else ActionStatus.FAILED
            )
            action.result = {"message": result.message, **result.details}
            action.rollback_token = result.rollback_token
        except Exception as exc:
            logger.exception("Executor failed for action %s", action_id)
            action.status = str(ActionStatus.FAILED)
            action.result = {"message": str(exc)}

        action.executed_by = executor_id
        action.executed_at = utcnow()
        action.approved_by = approved_by
        await self.db.flush()

        await self.timeline.record(
            incident_id=action.incident_id,
            actor_id=executor_id,
            action="action_executed",
            detail=f"{action.action_type} on {action.target}: {action.status}",
            metadata=action.result,
        )

        incident = await self.incidents.get(action.incident_id)
        if IncidentStatus(incident.status) == IncidentStatus.DECIDED:
            await self.incidents.transition(
                action.incident_id,
                IncidentStatus.ACTION_EXECUTED,
                actor_id=executor_id,
                note="Response action executed",
            )

        await event_bus.publish(
            DomainEvent(
                ACTION_EXECUTED,
                {
                    "action_id": action.id,
                    "incident_id": action.incident_id,
                    "action_type": action.action_type,
                    "status": action.status,
                    "dry_run": action.dry_run,
                },
            )
        )
        return action

    def _executor_for(self, action_type: ActionType, *, dry_run: bool) -> BaseExecutor:
        if dry_run:
            return NoopExecutor()
        for executor in self.executors:
            if executor.supports(action_type):
                return executor
        return NoopExecutor()

    async def for_incident(self, incident_id: str) -> list[ResponseActionModel]:
        return await self.repo.for_incident(incident_id)
