"""Pulls public threat feeds (MITRE ATT&CK, AbuseIPDB, custom).

TODO: implement per-feed adapters under infrastructure/feeds/ and schedule
this from workers/schedules.py. Respect each feed's rate limits and licence terms;
store the source and fetch time on every indicator for provenance.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class FeedSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def sync_all(self) -> dict[str, int]:
        logger.info("Feed sync not yet implemented")
        return {}
