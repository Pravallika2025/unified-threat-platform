from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.normalization.infrastructure.repository import NormalizedEventRepository
from app.modules.normalization.schemas import NormalizedEventOut

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/events", tags=["events"])


@router.get("/recent", response_model=list[NormalizedEventOut])
async def recent_events(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.DATA_VIEW)),
):
    return await NormalizedEventRepository(db).recent(min(limit, 200))
