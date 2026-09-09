from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.threat_intel.application.intel_service import IntelService
from app.modules.threat_intel.infrastructure.models import IndicatorModel
from app.modules.threat_intel.schemas import IndicatorCreate, IndicatorOut

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/threat-intel", tags=["threat-intel"])


@router.get("/indicators", response_model=list[IndicatorOut])
async def list_indicators(
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.ALERT_VIEW)),
):
    return await IntelService(db).list()


@router.post("/indicators", status_code=201)
async def add_indicators(
    data: list[IndicatorCreate],
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    added = await IntelService(db).add(
        [
            IndicatorModel(
                value=i.value.lower(),
                type=str(i.type),
                source=i.source,
                confidence=i.confidence,
                severity=i.severity,
                description=i.description,
            )
            for i in data
        ]
    )
    return {"added": added}
