from dataclasses import dataclass

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security.jwt import decode_token
from app.core.security.permissions import Permission, Role, has_permission

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: str
    role: Role
    environment_id: str | None

    def can(self, permission: Permission) -> bool:
        return has_permission(self.role, permission)


async def get_current_user(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    if creds is None:
        raise AuthenticationError("Missing bearer token")

    payload = decode_token(creds.credentials)
    user = CurrentUser(
        id=payload["sub"],
        role=Role(payload["role"]),
        environment_id=payload.get("env"),
    )
    request.state.user_id = user.id  # picked up by audit middleware
    return user


def require_permission(permission: Permission):
    async def _guard(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not user.can(permission):
            raise PermissionDeniedError(
                f"Role '{user.role}' lacks permission '{permission}'",
                details={"required": str(permission)},
            )
        return user

    return _guard


def require_role(*roles: Role):
    async def _guard(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise PermissionDeniedError(f"Requires one of: {[str(r) for r in roles]}")
        return user

    return _guard
