from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.incidents.schemas import IncidentOut
from app.modules.review.application.decision_service import DecisionService
from app.modules.review.application.review_queue_service import ReviewQueueService
from app.modules.review.schemas import DecisionCreate, DecisionOut

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/review", tags=["review"])


@router.get("/queue", response_model=list[IncidentOut])
async def queue(
    mine_only: bool = False,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission(Permission.INCIDENT_VIEW)),
):
    return await ReviewQueueService(db).queue(
        assigned_to=user.id if mine_only else None, limit=limit
    )


@router.post("/decisions", response_model=DecisionOut, status_code=201)
async def record_decision(
    data: DecisionCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission(Permission.DECISION_RECOMMEND)),
):
    return await DecisionService(db).record(
        incident_id=data.incident_id,
        analyst_id=user.id,
        action=data.action,
        justification=data.justification,
    )


@router.get("/decisions/pending", response_model=list[DecisionOut])
async def pending_approvals(
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.DECISION_APPROVE)),
):
    """Destructive decisions waiting on a second authoriser."""
    return await DecisionService(db).pending_approval()


@router.post("/decisions/{decision_id}/approve", response_model=DecisionOut)
async def approve_decision(
    decision_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission(Permission.DECISION_APPROVE)),
):
    return await DecisionService(db).approve(decision_id, approver_id=user.id)


@router.get("/decisions/{incident_id}", response_model=list[DecisionOut])
async def decisions_for_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.INCIDENT_VIEW)),
):
    return await DecisionService(db).for_incident(incident_id)
