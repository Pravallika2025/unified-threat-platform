import asyncio
from unittest.mock import AsyncMock, patch
import pytest

from app.workers.scheduler import AsyncScheduler


@pytest.mark.asyncio
async def test_scheduler_lifecycle():
    scheduler = AsyncScheduler(interval_seconds=1)
    with patch("app.workers.scheduler.pipeline_tick", new_callable=AsyncMock) as mock_tick, \
         patch("app.workers.scheduler.sync_threat_intel_feeds", new_callable=AsyncMock) as mock_sync, \
         patch("app.workers.scheduler.enforce_retention", new_callable=AsyncMock) as mock_retention:
        
        mock_tick.return_value = {"normalized": 2, "alerts": 1}
        mock_sync.return_value = {"AbuseIPDB": 5}
        mock_retention.return_value = {"pruned_raw": 0}

        scheduler.start()
        assert scheduler._running is True

        # Let the loop tick once
        await asyncio.sleep(2.5)

        await scheduler.stop()
        assert scheduler._running is False
        assert mock_tick.called
        assert mock_sync.called
        assert mock_retention.called
