from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.incidents.application.evidence_service import EvidenceService
from app.modules.incidents.application.incident_service import IncidentService
from app.modules.incidents.application.timeline_service import TimelineService
from app.modules.incidents.schemas import (
    AssignRequest,
    IncidentDetailOut,
    IncidentOut,
    TransitionRequest,
)

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentOut])
async def list_incidents(
    status: str | None = None,
    environment_id: str | None = None,
    assigned_to: str | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission(Permission.INCIDENT_VIEW)),
):
    # An environment-scoped user only ever sees their own environment.
    if user.environment_id:
        environment_id = user.environment_id
    return await IncidentService(db).list(
        status=status, environment_id=environment_id, assigned_to=assigned_to, limit=limit
    )


@router.get("/{incident_id}", response_model=IncidentDetailOut)
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.INCIDENT_VIEW)),
):
    service = IncidentService(db)
    incident = await service.get(incident_id)
    detail = IncidentDetailOut.model_validate(incident, from_attributes=True)
    detail.evidence = [
        e for e in await EvidenceService(db).list(incident_id)
    ]  # pydantic coerces via from_attributes
    detail.timeline = [t for t in await TimelineService(db).list(incident_id)]
    return detail


@router.post("/from-alert/{alert_id}", response_model=IncidentOut, status_code=201)
async def create_from_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.INCIDENT_INVESTIGATE)),
):
    return await IncidentService(db).create_from_alert(alert_id)


@router.post("/{incident_id}/transition", response_model=IncidentOut)
async def transition(
    incident_id: str,
    data: TransitionRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission(Permission.INCIDENT_INVESTIGATE)),
):
    return await IncidentService(db).transition(
        incident_id, data.target, actor_id=user.id, note=data.note
    )


@router.post("/{incident_id}/assign", response_model=IncidentOut)
async def assign(
    incident_id: str,
    data: AssignRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission(Permission.INCIDENT_ASSIGN)),
):
    return await IncidentService(db).assign(incident_id, data.analyst_id, actor_id=user.id)


@router.get("/{incident_id}/evidence/verify")
async def verify_evidence(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.AUDIT_VIEW)),
):
    """Recomputes every evidence hash. Anything reported as not intact was altered
    outside the application."""
    return {"results": await EvidenceService(db).verify(incident_id)}
