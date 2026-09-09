"""Groups alerts that describe one campaign rather than N unrelated events.

Features:
1. Same-entity clustering inside a time window.
2. Cross-environment correlation (same source IP / threat actor hitting multiple environments).
3. Kill-chain narrative synthesis via KillChainBuilder.
"""

from collections import defaultdict
from datetime import timedelta
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.correlation.application.kill_chain_builder import KillChainBuilder
from app.modules.correlation.domain.entities import EventCluster, KillChainNarrative
from app.modules.detection.infrastructure.repository import AlertRepository
from app.shared.types import as_utc, utcnow

logger = logging.getLogger(__name__)


class CorrelationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.alerts = AlertRepository(db)
        self.kill_chain_builder = KillChainBuilder()

    async def cluster_recent(
        self, *, environment_id: str, window_minutes: int = 60
    ) -> list[EventCluster]:
        """Clusters alerts for a single environment within a rolling window."""
        since = utcnow() - timedelta(minutes=window_minutes)
        alerts = [
            a
            for a in await self.alerts.list(environment_id=environment_id, limit=500)
            if as_utc(a.created_at) >= since
        ]

        grouped: dict[str, list[Any]] = defaultdict(list)
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
                    span_minutes=max(1, int(span.total_seconds() // 60)),
                    environment_id=environment_id,
                    environments_hit=[environment_id],
                )
            )

        clusters.sort(key=lambda c: len(c.alert_ids), reverse=True)
        return clusters

    async def cluster_cross_environment(self, *, window_minutes: int = 120) -> list[EventCluster]:
        """Identifies global campaigns hitting multiple distinct environments."""
        since = utcnow() - timedelta(minutes=window_minutes)
        all_alerts = [
            a
            for a in await self.alerts.list(limit=1000)
            if as_utc(a.created_at) >= since
        ]

        grouped: dict[str, list[Any]] = defaultdict(list)
        for alert in all_alerts:
            grouped[alert.entity].append(alert)

        cross_clusters = []
        for entity, entity_alerts in grouped.items():
            envs = list({a.environment_id for a in entity_alerts if a.environment_id})
            if len(envs) > 1 or len(entity_alerts) >= 3:
                entity_alerts.sort(key=lambda a: as_utc(a.created_at))
                span = as_utc(entity_alerts[-1].created_at) - as_utc(entity_alerts[0].created_at)
                cross_clusters.append(
                    EventCluster(
                        entity=entity,
                        alert_ids=[a.id for a in entity_alerts],
                        tactics=[a.attack_tactic for a in entity_alerts if a.attack_tactic],
                        span_minutes=max(1, int(span.total_seconds() // 60)),
                        environment_id=None,
                        environments_hit=envs,
                    )
                )

        cross_clusters.sort(key=lambda c: len(c.alert_ids), reverse=True)
        return cross_clusters

    async def build_narrative_for_cluster(self, cluster: EventCluster) -> KillChainNarrative:
        """Constructs an analyst-ready narrative for an EventCluster."""
        alerts = []
        for aid in cluster.alert_ids:
            a = await self.alerts.get(aid)
            if a:
                alerts.append(a)
        return self.kill_chain_builder.build_narrative(alerts, cluster.entity)
