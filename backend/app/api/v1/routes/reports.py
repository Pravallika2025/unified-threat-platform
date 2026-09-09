from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.reports.application.report_service import ReportService

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/reports", tags=["reports"])


@router.get("/incidents")
async def incident_report(
    format: str = "json",
    environment_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.REPORT_GENERATE)),
):
    content, media_type = await ReportService(db).incident_report(
        fmt=format, environment_id=environment_id
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="incidents.{format}"'},
    )


@router.get("/executive-summary")
async def executive_summary(
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.REPORT_VIEW)),
):
    return await ReportService(db).executive_summary()
