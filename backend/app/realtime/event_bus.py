"""Optional Redis bridge so WebSocket broadcasts reach every API instance.

TODO: subscribe to a Redis channel on startup and re-broadcast into
ConnectionManager. Without this, a two-instance deployment behind a load balancer
only notifies the instance that produced the event.
"""

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


async def start_redis_bridge() -> None:
    if not settings.REDIS_URL:
        logger.info("REDIS_URL not set — running realtime in single-instance mode")
        return
    logger.info("Redis bridge not yet implemented; realtime stays single-instance")
