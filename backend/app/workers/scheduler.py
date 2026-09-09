"""Asynchronous background scheduler for continuous threat detection and platform automation.

Runs tasks periodically without requiring external worker infrastructure:
- pipeline_tick: Ingestion log normalization, rule evaluation, anomaly/behavior detection, and incident creation.
- sync_threat_intel_feeds: Periodic update of threat intelligence IOCs from configured feeds.
- enforce_retention: Daily data retention and lifecycle pruning while protecting the immutable audit log.
"""

import asyncio
from datetime import datetime, timezone
import logging
from typing import Optional

from app.core.config import settings
from app.workers.tasks.pipeline_tasks import (
    enforce_retention,
    pipeline_tick,
    sync_threat_intel_feeds,
)

logger = logging.getLogger(__name__)


class AsyncScheduler:
    def __init__(self, interval_seconds: int = 60):
        self.interval_seconds = interval_seconds
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._last_feed_sync: Optional[datetime] = None
        self._last_retention: Optional[datetime] = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop(), name="threat-platform-scheduler")
        logger.info("AsyncScheduler started with tick interval of %d seconds", self.interval_seconds)

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("AsyncScheduler stopped")

    async def _run_loop(self) -> None:
        # Initial small delay to let database migrations/startup stabilize
        await asyncio.sleep(2)

        while self._running:
            try:
                await self._tick()
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Unexpected error in AsyncScheduler loop")

            try:
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                break

    async def _tick(self) -> None:
        now = datetime.now(timezone.utc)

        # 1. Pipeline tick (every tick interval, e.g. 60s)
        try:
            res = await pipeline_tick()
            if res.get("normalized", 0) > 0 or res.get("alerts", 0) > 0:
                logger.info("Scheduler pipeline tick: normalized=%d, alerts=%d", res.get("normalized", 0), res.get("alerts", 0))
        except Exception:
            logger.exception("Scheduler pipeline_tick failed")

        # 2. Threat Intel Feed Sync (every 6 hours)
        if self._last_feed_sync is None or (now - self._last_feed_sync).total_seconds() >= 21600:
            try:
                sync_res = await sync_threat_intel_feeds()
                self._last_feed_sync = now
                logger.info("Scheduler feed sync finished: %s", sync_res)
            except Exception:
                logger.exception("Scheduler sync_threat_intel_feeds failed")

        # 3. Retention enforcement (every 24 hours)
        if self._last_retention is None or (now - self._last_retention).total_seconds() >= 86400:
            try:
                ret_res = await enforce_retention()
                self._last_retention = now
                logger.info("Scheduler retention enforcement finished: %s", ret_res)
            except Exception:
                logger.exception("Scheduler enforce_retention failed")


scheduler = AsyncScheduler(interval_seconds=settings.SCHEDULER_INTERVAL_SECONDS)
