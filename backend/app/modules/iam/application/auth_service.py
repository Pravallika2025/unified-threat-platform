import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.security.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security.mfa import verify_totp
from app.core.security.password import verify_password
from app.core.security.permissions import Role
from app.modules.iam.infrastructure.models import UserModel
from app.modules.iam.infrastructure.repository import UserRepository
from app.modules.iam.schemas import TokenResponse
from app.shared.types import utcnow

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)

    async def login(self, email: str, password: str, totp_code: str | None) -> TokenResponse:
        user = await self.users.get_by_email(email)

        # Same error and roughly the same work either way — no user enumeration.
        if user is None or not verify_password(password, user.password_hash):
            logger.info("Failed login attempt for %s", email)
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is disabled")

        if user.mfa_enabled:
            if not totp_code:
                raise AuthenticationError("MFA code required")
            if not verify_totp(user.mfa_secret or "", totp_code):
                raise AuthenticationError("Invalid MFA code")

        user.last_login_at = utcnow()
        await self.db.flush()

        return self._issue(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token, expected_type="refresh")
        user = await self.users.get(payload["sub"])
        if user is None or not user.is_active:
            raise AuthenticationError("User no longer valid")
        return self._issue(user)

    def _issue(self, user: UserModel) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(
                user_id=user.id, role=Role(user.role), environment_id=user.environment_id
            ),
            refresh_token=create_refresh_token(user_id=user.id),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
