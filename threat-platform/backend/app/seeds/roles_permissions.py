"""The bootstrap admin. Everything else is created through the UI.

The password comes from FIRST_ADMIN_PASSWORD and must be changed on first login
in any real deployment.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security.password import hash_password
from app.core.security.permissions import Role
from app.modules.iam.infrastructure.models import UserModel
from app.modules.iam.infrastructure.repository import UserRepository

logger = logging.getLogger(__name__)


async def seed_admin(db: AsyncSession) -> UserModel | None:
    repo = UserRepository(db)
    if await repo.get_by_email(settings.FIRST_ADMIN_EMAIL):
        logger.info("Admin already exists, skipping")
        return None

    admin = await repo.add(
        UserModel(
            email=settings.FIRST_ADMIN_EMAIL.lower(),
            full_name="Platform Administrator",
            password_hash=hash_password(settings.FIRST_ADMIN_PASSWORD),
            role=str(Role.SUPER_ADMIN),
        )
    )
    logger.info("Created bootstrap admin: %s", admin.email)
    return admin
