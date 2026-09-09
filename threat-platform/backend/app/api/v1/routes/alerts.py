from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.detection.application.detection_orchestrator import DetectionOrchestrator
from app.modules.detection.application.rule_loader import rule_loader
from app.modules.detection.infrastructure.repository import AlertRepository
from app.modules.detection.schemas import AlertOut, RunDetectionRequest
from app.modules.incidents.application.incident_service import IncidentService

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
async def list_alerts(
    environment_id: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.ALERT_VIEW)),
):
    return await AlertRepository(db).list(
        environment_id=environment_id, severity=severity, status=status, limit=limit
    )


@router.post("/detect", response_model=list[AlertOut])
async def run_detection(
    data: RunDetectionRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.INCIDENT_INVESTIGATE)),
):
    """Stage 3 on demand. Auto-opens incidents for anything above the risk threshold."""
    alerts = await DetectionOrchestrator(db).run(
        environment_id=data.environment_id, lookback_minutes=data.lookback_minutes
    )
    await IncidentService(db).auto_open_for_high_risk(alerts)
    return alerts


@router.get("/rules")
async def list_rules(_: CurrentUser = Depends(require_permission(Permission.ALERT_VIEW))):
    return [
        {
            "id": r.id,
            "title": r.title,
            "severity": str(r.severity),
            "type": str(r.rule_type),
            "environments": r.environments,
            "attack": r.attack,
            "enabled": r.enabled,
        }
        for r in rule_loader.load_all()
    ]


@router.post("/rules/reload")
async def reload_rules(_: CurrentUser = Depends(require_permission(Permission.SETTINGS_MANAGE))):
    """Pick up edits to detection-content/ without restarting the service."""
    return {"loaded": rule_loader.reload()}
