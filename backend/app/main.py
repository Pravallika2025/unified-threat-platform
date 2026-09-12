import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import create_all
from app.core.exception_handlers import register_exception_handlers
from app.core.logging_config import configure_logging
from app.core.middleware.rate_limit import RateLimitMiddleware
from app.core.middleware.request_id import RequestIdMiddleware
from app.core.middleware.security_headers import SecurityHeadersMiddleware
from app.modules.detection.application.rule_loader import rule_loader
from app.modules.notifications.application.notification_service import (
    register_notification_handlers,
)
from app.realtime import ws_routes
from app.realtime.event_bus import start_redis_bridge
from app.workers.scheduler import scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting %s (%s)", settings.APP_NAME, settings.ENVIRONMENT)

    if settings.AUTO_CREATE_TABLES:
        await create_all()

    count = len(rule_loader.load_all())
    logger.info("Detection rules loaded: %d", count)

    register_notification_handlers()
    await start_redis_bridge()

    if settings.ENABLE_BACKGROUND_SCHEDULER:
        scheduler.start()

    yield
    logger.info("Shutting down")
    if settings.ENABLE_BACKGROUND_SCHEDULER:
        await scheduler.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Unified multi-environment cyber threat detection and response platform. "
            "Authorized ingestion, detection, risk scoring, human-reviewed response, "
            "and a tamper-evident audit trail."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestIdMiddleware)

    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    app.include_router(ws_routes.router)

    return app


app = create_app()
