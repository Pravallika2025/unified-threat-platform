from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.security.permissions import Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: Role
    environment_id: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: Role
    environment_id: str | None
    is_active: bool
    mfa_enabled: bool
    created_at: datetime
    last_login_at: datetime | None


class MeOut(UserOut):
    permissions: list[str]
