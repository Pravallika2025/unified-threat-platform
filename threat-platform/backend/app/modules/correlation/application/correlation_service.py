"""Groups alerts that describe one campaign rather than N unrelated events.

Implemented: same-entity clustering inside a time window.
TODO: cross-entity correlation (same source IP hitting three environments),
and promoting a cluster into a single incident instead of several.
"""

import logging
from collections import defaultdict
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.correlation.domain.entities import EventCluster
from app.modules.detection.infrastructure.repository import AlertRepository
from app.shared.types import as_utc, utcnow

logger = logging.getLogger(__name__)


class CorrelationService:
    def __init__(self, db: AsyncSession):
        self.alerts = AlertRepository(db)

    async def cluster_recent(
        self, *, environment_id: str, window_minutes: int = 60
    ) -> list[EventCluster]:
        since = utcnow() - timedelta(minutes=window_minutes)
        alerts = [
            a
            for a in await self.alerts.list(environment_id=environment_id, limit=500)
            if as_utc(a.created_at) >= since
        ]

        grouped: dict[str, list] = defaultdict(list)
        for alert in alerts:
            grouped[alert.entity].append(alert)

        clusters = []
        for entity, entity_alerts in grouped.items():
            if len(entity_alerts) < 2:
                continue
            entity_alerts.sort(key=lambda a: as_utc(a.created_at))
            span = as_utc(entity_alerts[-1].created_at) - as_utc(entity_alerts[0].created_at)
            clusters.append(
                EventCluster(
                    entity=entity,
                    alert_ids=[a.id for a in entity_alerts],
                    tactics=[a.attack_tactic for a in entity_alerts if a.attack_tactic],
                    span_minutes=int(span.total_seconds() // 60),
                )
            )

        clusters.sort(key=lambda c: len(c.alert_ids), reverse=True)
        return clusters
