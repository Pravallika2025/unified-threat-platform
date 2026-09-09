"""Threat Intelligence Feed Synchronization Service.

Pulls indicators from registered feeds (AbuseIPDB, MITRE ATT&CK, Custom),
de-duplicates by value + source against the database, and stores new IOCs.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.threat_intel.infrastructure.feeds.abuseipdb_feed import AbuseIPDBFeed
from app.modules.threat_intel.infrastructure.feeds.custom_feed import CustomFeed
from app.modules.threat_intel.infrastructure.feeds.mitre_attack_feed import MitreAttackFeed
from app.modules.threat_intel.infrastructure.models import IndicatorModel
from app.modules.threat_intel.infrastructure.repository import IndicatorRepository

logger = logging.getLogger(__name__)


class FeedSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IndicatorRepository(db)
        self.feeds = [
            AbuseIPDBFeed(),
            MitreAttackFeed(),
            CustomFeed(),
        ]

    async def sync_all(self) -> dict[str, int]:
        """Runs all registered feed providers and persists new unique indicators."""
        results: dict[str, int] = {}
        existing_rows = (await self.db.execute(select(IndicatorModel.value, IndicatorModel.source))).all()
        existing_set = {(r[0].lower(), r[1]) for r in existing_rows}

        total_added = 0
        for feed in self.feeds:
            try:
                indicators = await feed.fetch()
                to_add = []
                for ind in indicators:
                    key = (ind.value.lower(), ind.source)
                    if key not in existing_set:
                        existing_set.add(key)
                        to_add.append(
                            IndicatorModel(
                                value=ind.value.lower(),
                                type=str(ind.type),
                                source=ind.source,
                                confidence=ind.confidence,
                                severity=ind.severity,
                                description=ind.description,
                            )
                        )

                if to_add:
                    await self.repo.add_many(to_add)
                    total_added += len(to_add)

                results[feed.name] = len(to_add)
                logger.info("Feed %s: synced %d new indicators", feed.name, len(to_add))
            except Exception as exc:
                logger.exception("Failed to sync feed %s: %s", feed.name, exc)
                results[feed.name] = 0

        results["total_added"] = total_added
        return results
