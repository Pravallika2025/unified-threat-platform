from dataclasses import dataclass
from datetime import datetime

from app.core.security.permissions import Role


@dataclass
class User:
    id: str
    email: str
    full_name: str
    role: Role
    environment_id: str | None
    is_active: bool
    mfa_enabled: bool
    created_at: datetime
    last_login_at: datetime | None = None
