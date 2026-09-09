from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.environments.application.environment_service import EnvironmentService
from app.modules.environments.schemas import EnvironmentCreate, EnvironmentOut

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/environments", tags=["environments"])


@router.get("", response_model=list[EnvironmentOut])
async def list_environments(
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.ENV_VIEW)),
):
    return await EnvironmentService(db).list()


@router.post("", response_model=EnvironmentOut, status_code=201)
async def create_environment(
    data: EnvironmentCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.ENV_MANAGE)),
):
    return await EnvironmentService(db).create(data)


@router.get("/{environment_id}", response_model=EnvironmentOut)
async def get_environment(
    environment_id: str,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.ENV_VIEW)),
):
    return await EnvironmentService(db).get(environment_id)
