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


from pydantic import BaseModel
from app.core.security.permissions import Role


class UserRoleUpdate(BaseModel):
    role: Role


@router.post("/{user_id}/activate", response_model=UserOut)
async def activate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.USER_MANAGE)),
):
    """Admin approves or re-activates an operator account."""
    return await UserService(db).set_active(user_id, True)


@router.post("/{user_id}/deactivate", response_model=UserOut)
async def deactivate(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.USER_MANAGE)),
):
    """Admin disables or suspends an account to prevent misuse."""
    return await UserService(db).set_active(user_id, False)


@router.post("/{user_id}/role", response_model=UserOut)
async def update_user_role(
    user_id: str,
    data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.USER_MANAGE)),
):
    """Admin changes operator role and permission tier."""
    return await UserService(db).set_role(user_id, data.role)


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.USER_MANAGE)),
):
    """Admin permanently removes an unauthorized account."""
    await UserService(db).delete(user_id)
    return {"status": "deleted", "user_id": user_id}

