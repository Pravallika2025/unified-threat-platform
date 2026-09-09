from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, get_current_user
from app.modules.dashboard.application.distribution_service import DistributionService
from app.modules.dashboard.application.env_status_service import EnvStatusService
from app.modules.dashboard.application.metrics_service import MetricsService
from app.modules.dashboard.application.timeseries_service import TimeseriesService
from app.modules.dashboard.schemas import DashboardOut
from app.modules.detection.infrastructure.repository import AlertRepository
from app.modules.detection.schemas import AlertOut

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOut)
async def overview(
    hours: int = 24,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    """Everything the single-screen dashboard needs, in one round trip."""
    return DashboardOut(
        kpis=await MetricsService(db).kpis(),
        threats_over_time=await TimeseriesService(db).threats_over_time(hours),
        severity_distribution=await DistributionService(db).by_severity(),
        top_sources=await DistributionService(db).top_sources(),
        environment_status=await EnvStatusService(db).statuses(),
    )


@router.get("/recent-alerts", response_model=list[AlertOut])
async def recent_alerts(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await AlertRepository(db).list(limit=limit)
