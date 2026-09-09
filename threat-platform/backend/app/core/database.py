from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Single declarative base. Every module's models.py inherits from this."""


engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


if settings.DATABASE_URL.startswith("sqlite"):

    @event.listens_for(Engine, "connect")
    def _sqlite_pragmas(dbapi_connection, _):
        """WAL lets readers and the writer coexist; the busy timeout stops a brief
        overlap from surfacing as 'database is locked'."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Yields the request's session and publishes it on request.state so
    UnitOfWorkRoute can audit and commit it before the response is sent.

    Callers outside the HTTP layer (workers, seeds, scripts) use SessionLocal
    directly and manage their own commits.
    """
    async with SessionLocal() as session:
        request.state.db = session
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def import_all_models() -> None:
    """Import every module's models so Base.metadata is complete before create_all."""
    from app.modules.audit.infrastructure import models as _audit  # noqa: F401
    from app.modules.detection.infrastructure import models as _detection  # noqa: F401
    from app.modules.environments.infrastructure import models as _env  # noqa: F401
    from app.modules.iam.infrastructure import models as _iam  # noqa: F401
    from app.modules.incidents.infrastructure import models as _inc  # noqa: F401
    from app.modules.ingestion.infrastructure import models as _ing  # noqa: F401
    from app.modules.normalization.infrastructure import models as _norm  # noqa: F401
    from app.modules.response.infrastructure import models as _resp  # noqa: F401
    from app.modules.review.infrastructure import models as _rev  # noqa: F401
    from app.modules.threat_intel.infrastructure import models as _ti  # noqa: F401


async def create_all() -> None:
    import_all_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
