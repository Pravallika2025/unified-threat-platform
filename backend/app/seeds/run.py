"""Idempotent bootstrap: python -m app.seeds.run"""

import asyncio
import logging

from app.core.config import settings
from app.core.database import SessionLocal, create_all
from app.core.logging_config import configure_logging
from app.seeds.demo_data import seed_demo
from app.seeds.roles_permissions import seed_admin

logger = logging.getLogger(__name__)


async def main() -> None:
    configure_logging()
    await create_all()

    async with SessionLocal() as db:
        await seed_admin(db)
        if settings.is_dev:
            await seed_demo(db)
        await db.commit()

    logger.info("Seed complete")
    print(f"\n  Login: {settings.FIRST_ADMIN_EMAIL} / {settings.FIRST_ADMIN_PASSWORD}")
    print("  Analyst: analyst@threatplatform.dev / Analyst@12345\n")


if __name__ == "__main__":
    asyncio.run(main())
