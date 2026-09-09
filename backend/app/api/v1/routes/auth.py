from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, get_current_user
from app.core.security.permissions import Role, permissions_for
from app.modules.iam.application.auth_service import AuthService
from app.modules.iam.application.user_service import UserService
from app.modules.iam.schemas import LoginRequest, MeOut, RegisterRequest, TokenResponse, UserCreate, UserOut

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).login(data.email, data.password, data.totp_code)


@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Public self-registration. New accounts are created as security_analyst."""
    create = UserCreate(
        email=data.email,
        full_name=data.full_name,
        password=data.password,
        role=Role.security_analyst,
    )
    # Pass super_admin as actor so the service does not block the role assignment.
    return await UserService(db).create(create, actor_role=Role.super_admin)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).refresh(refresh_token)


@router.get("/me", response_model=MeOut)
async def me(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    record = await UserService(db).get(user.id)
    return MeOut(
        id=record.id,
        email=record.email,
        full_name=record.full_name,
        role=record.role,
        environment_id=record.environment_id,
        is_active=record.is_active,
        mfa_enabled=record.mfa_enabled,
        created_at=record.created_at,
        last_login_at=record.last_login_at,
        permissions=sorted(str(p) for p in permissions_for(user.role)),
    )
