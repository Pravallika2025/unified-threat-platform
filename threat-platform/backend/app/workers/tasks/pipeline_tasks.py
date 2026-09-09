"""The pipeline as scheduled work.

Each function is plain async so it can be called from Celery, from a test, or
from the HTTP endpoints — the logic lives in the services, not here.
"""

import logging

from app.core.database import SessionLocal
from app.modules.detection.application.detection_orchestrator import DetectionOrchestrator
from app.modules.environments.application.environment_service import EnvironmentService
from app.modules.incidents.application.incident_service import IncidentService
from app.modules.normalization.application.normalizer_service import NormalizerService

logger = logging.getLogger(__name__)


async def normalize_pending() -> int:
    async with SessionLocal() as db:
        count = await NormalizerService(db).process_pending()
        await db.commit()
        return count


async def run_detection_all_environments(lookback_minutes: int = 15) -> int:
    total = 0
    async with SessionLocal() as db:
        environments = await EnvironmentService(db).list()
        for env in environments:
            alerts = await DetectionOrchestrator(db).run(
                environment_id=env.id, lookback_minutes=lookback_minutes
            )
            await IncidentService(db).auto_open_for_high_risk(alerts)
            total += len(alerts)
        await db.commit()
    logger.info("Scheduled detection produced %d alerts", total)
    return total


async def pipeline_tick() -> dict:
    """Normalize then detect. Run this every minute."""
    normalized = await normalize_pending()
    alerts = await run_detection_all_environments()
    return {"normalized": normalized, "alerts": alerts}
