from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.response.application.response_orchestrator import ResponseOrchestrator
from app.modules.response.schemas import ActionOut, ActionRequest

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/response", tags=["response"])


@router.post("/actions", response_model=ActionOut, status_code=201)
async def request_action(
    data: ActionRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission(Permission.DECISION_RECOMMEND)),
):
    """Requesting is not executing. Destructive actions land in pending_approval."""
    return await ResponseOrchestrator(db).request(
        incident_id=data.incident_id,
        decision_id=data.decision_id,
        action_type=data.action_type,
        target=data.target,
        params=data.params,
        requested_by=user.id,
        dry_run=data.dry_run,
    )


@router.post("/actions/{action_id}/execute", response_model=ActionOut)
async def execute_action(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission(Permission.RESPONSE_EXECUTE)),
):
    """Passes through ApprovalGate. A destructive action without an approved decision
    returns 428 and changes nothing."""
    return await ResponseOrchestrator(db).execute(action_id, executor_id=user.id)


@router.get("/actions/{incident_id}", response_model=list[ActionOut])
async def actions_for_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.INCIDENT_VIEW)),
):
    return await ResponseOrchestrator(db).for_incident(incident_id)
