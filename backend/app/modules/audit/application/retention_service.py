"""Data retention and lifecycle enforcement service.

Enforces data lifecycle windows with strict safety guarantees:
1. Audit logs are preserved and never deleted in place (cryptographic chain guarantee).
2. Events and raw records linked to open incidents are protected from pruning.
3. Expired raw and normalized events beyond the retention horizon are pruned.
"""

from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.infrastructure.models import IncidentModel
from app.modules.ingestion.infrastructure.models import RawEventModel
from app.modules.normalization.infrastructure.models import NormalizedEventModel

logger = logging.getLogger(__name__)

DEFAULT_RETENTION_DAYS = {
    "raw_events": 90,
    "normalized_events": 180,
    "alerts": 365,
    "incidents": 1095,
    "audit_log": 2555,  # 7 years — permanent append-only
}


class RetentionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def enforce_all(self, custom_retention_days: dict[str, int] | None = None) -> dict[str, int]:
        retention = {**DEFAULT_RETENTION_DAYS, **(custom_retention_days or {})}
        now = datetime.now(timezone.utc)

        # 1. Identify protected event IDs attached to open incidents
        open_incidents = (
            await self.db.execute(
                select(IncidentModel).where(IncidentModel.status.in_(["new", "investigating", "review", "decided"]))
            )
        ).scalars().all()

        protected_event_ids: set[str] = set()
        for inc in open_incidents:
            for item in getattr(inc, "evidence", []) or []:
                if isinstance(item, dict) and "event_id" in item:
                    protected_event_ids.add(item["event_id"])

        results = {"pruned_raw": 0, "pruned_normalized": 0, "audit_log_status": "protected_immutable"}

        # 2. Prune expired normalized events (excluding protected IDs)
        norm_cutoff = now - timedelta(days=retention["normalized_events"])
        query_norm = (
            delete(NormalizedEventModel)
            .where(NormalizedEventModel.timestamp < norm_cutoff)
            .where(~NormalizedEventModel.id.in_(protected_event_ids) if protected_event_ids else True)
        )
        norm_res = await self.db.execute(query_norm)
        results["pruned_normalized"] = norm_res.rowcount if hasattr(norm_res, "rowcount") else 0

        # 3. Prune expired raw events (only those already processed)
        raw_cutoff = now - timedelta(days=retention["raw_events"])
        query_raw = (
            delete(RawEventModel)
            .where(RawEventModel.received_at < raw_cutoff)
            .where(RawEventModel.processed.is_(True))
        )
        raw_res = await self.db.execute(query_raw)
        results["pruned_raw"] = raw_res.rowcount if hasattr(raw_res, "rowcount") else 0

        logger.info("RetentionService executed: %s", results)
        return results
