from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Single declarative base. Every module's models.py inherits from this."""


engine_kwargs = {"echo": False, "future": True}

if settings.DATABASE_URL.startswith("sqlite"):
    pass
else:
    engine_kwargs.update(
        {
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_timeout": settings.DB_POOL_TIMEOUT,
            "pool_recycle": settings.DB_POOL_RECYCLE,
            "pool_pre_ping": True,
        }
    )

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)
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
    import importlib

    for mod in [
        "app.modules.audit.infrastructure.models",
        "app.modules.detection.infrastructure.models",
        "app.modules.environments.infrastructure.models",
        "app.modules.iam.infrastructure.models",
        "app.modules.incidents.infrastructure.models",
        "app.modules.ingestion.infrastructure.models",
        "app.modules.normalization.infrastructure.models",
        "app.modules.response.infrastructure.models",
        "app.modules.review.infrastructure.models",
        "app.modules.threat_intel.infrastructure.models",
    ]:
        importlib.import_module(mod)


async def create_all() -> None:
    import_all_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
