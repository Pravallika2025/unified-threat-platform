import pytest

from app.modules.threat_intel.domain.entities import IndicatorType
from app.modules.threat_intel.infrastructure.feeds.abuseipdb_feed import AbuseIPDBFeed
from app.modules.threat_intel.infrastructure.feeds.custom_feed import CustomFeed
from app.modules.threat_intel.infrastructure.feeds.mitre_attack_feed import MitreAttackFeed


@pytest.mark.asyncio
async def test_abuseipdb_feed_fetch():
    feed = AbuseIPDBFeed()
    indicators = await feed.fetch()
    assert len(indicators) > 0
    assert any(i.type == IndicatorType.IP for i in indicators)
    assert any(i.value == "203.0.113.77" for i in indicators)


@pytest.mark.asyncio
async def test_mitre_attack_feed_fetch():
    feed = MitreAttackFeed()
    indicators = await feed.fetch()
    assert len(indicators) > 0
    assert any(i.type == IndicatorType.HASH for i in indicators)


@pytest.mark.asyncio
async def test_custom_feed_fetch():
    feed = CustomFeed([{"value": "bad-actor.net", "type": "domain", "confidence": 99}])
    indicators = await feed.fetch()
    assert any(i.value == "bad-actor.net" for i in indicators)
