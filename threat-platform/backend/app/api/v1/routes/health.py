from fastapi import APIRouter

from app.core.unit_of_work import UnitOfWorkRoute
from app.core.config import settings
from app.realtime.connection_manager import manager

router = APIRouter(route_class=UnitOfWorkRoute, tags=["health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "websocket_connections": manager.count,
    }
