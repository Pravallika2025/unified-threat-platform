"""Background workers.

Optional in development — every pipeline stage also has an on-demand HTTP endpoint.
Enable this when you want the pipeline to run continuously.

  celery -A app.workers.celery_app worker --loglevel=info
  celery -A app.workers.celery_app beat  --loglevel=info
"""

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from celery import Celery

    celery_app = Celery(
        "threat_platform",
        broker=settings.REDIS_URL or "memory://",
        backend=settings.REDIS_URL or "cache+memory://",
    )
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
    )
except ImportError:  # celery is not a hard dependency
    celery_app = None
    logger.info("Celery not installed — background scheduling disabled")
