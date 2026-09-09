import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.environments.application.environment_service import EnvironmentService
from app.modules.ingestion.application.consent_guard import ConsentGuard
from app.modules.ingestion.domain.entities import IngestResult
from app.modules.ingestion.domain.source_type import SourceType
from app.modules.ingestion.infrastructure.models import RawEventModel
from app.modules.ingestion.infrastructure.repository import RawEventRepository
from app.shared.events import EVENT_INGESTED, DomainEvent, event_bus
from app.shared.types import new_id

logger = logging.getLogger(__name__)

MAX_BATCH = 5000


class IngestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RawEventRepository(db)
        self.environments = EnvironmentService(db)

    async def ingest(
        self,
        *,
        environment_id: str,
        source_type: SourceType,
        records: list[dict[str, Any]],
        uploaded_by: str | None = None,
    ) -> IngestResult:
        env = await self.environments.get(environment_id)

        # Charter principle 1 — authorized sources only.
        ConsentGuard(env.authorized_sources).assert_allowed(source_type, env.name)

        batch_id = new_id()
        accepted, rejected, reasons = [], 0, []

        for record in records[:MAX_BATCH]:
            if not isinstance(record, dict) or not record:
                rejected += 1
                reasons.append("Record is empty or not an object")
                continue
            accepted.append(
                RawEventModel(
                    environment_id=environment_id,
                    source_type=str(source_type),
                    payload=record,
                    batch_id=batch_id,
                    uploaded_by=uploaded_by,
                )
            )

        if len(records) > MAX_BATCH:
            over = len(records) - MAX_BATCH
            rejected += over
            reasons.append(f"{over} records dropped: batch limit is {MAX_BATCH}")

        await self.repo.add_many(accepted)

        await event_bus.publish(
            DomainEvent(
                EVENT_INGESTED,
                {"batch_id": batch_id, "environment_id": environment_id, "count": len(accepted)},
            )
        )
        logger.info("Ingested %d records into %s (batch %s)", len(accepted), env.name, batch_id)

        return IngestResult(
            batch_id=batch_id,
            accepted=len(accepted),
            rejected=rejected,
            reasons=list(dict.fromkeys(reasons))[:10],
        )
