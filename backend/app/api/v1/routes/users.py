from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.iam.application.user_service import UserService
from app.modules.iam.schemas import UserCreate, UserOut

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
async def list_users(
    environment_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.USER_VIEW)),
):
    return await UserService(db).list(environment_id)


@router.post("", response_model=UserOut, status_code=201)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission(Permission.USER_MANAGE)),
):
    return await UserService(db).create(data, actor_role=user.role)


@router.post("/{user_id}/deactivate", response_model=UserOut)
async def deactivate(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.USER_MANAGE)),
):
    return await UserService(db).set_active(user_id, False)
