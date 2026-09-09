from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.correlation.application.correlation_service import CorrelationService
from app.modules.correlation.schemas import ClusterOut
from app.modules.incidents.application.evidence_service import EvidenceService

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/investigation", tags=["investigation"])


@router.get("/clusters", response_model=list[ClusterOut])
async def clusters(
    environment_id: str,
    window_minutes: int = 60,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.INCIDENT_INVESTIGATE)),
):
    """Alerts grouped by entity — turns 40 alerts into 3 stories."""
    found = await CorrelationService(db).cluster_recent(
        environment_id=environment_id, window_minutes=window_minutes
    )
    return [
        ClusterOut(
            entity=c.entity,
            alert_ids=c.alert_ids,
            tactics=c.tactics,
            span_minutes=c.span_minutes,
            progresses_kill_chain=c.progresses_kill_chain,
        )
        for c in found
    ]


@router.post("/{incident_id}/notes", status_code=201)
async def add_note(
    incident_id: str,
    note: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission(Permission.INCIDENT_INVESTIGATE)),
):
    """Analyst notes are stored as evidence — hashed and immutable, like everything else."""
    evidence = await EvidenceService(db).attach(
        incident_id=incident_id, kind="note", content={"note": note}, collected_by=user.id
    )
    return {"evidence_id": evidence.id, "content_hash": evidence.content_hash}
