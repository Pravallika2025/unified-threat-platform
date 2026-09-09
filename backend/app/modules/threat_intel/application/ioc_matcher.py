from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.threat_intel.infrastructure.repository import IndicatorRepository


async def build_ioc_index(db: AsyncSession) -> dict[str, dict]:
    """Flat lookup table consumed by SignatureEngine.

    TODO: cache in Redis with a TTL once the indicator set grows past ~100k.
    """
    indicators = await IndicatorRepository(db).all()
    return {
        indicator.value.lower(): {
            "type": indicator.type,
            "source": indicator.source,
            "severity": indicator.severity,
            "confidence": indicator.confidence,
            "attack": indicator.attack or {},
        }
        for indicator in indicators
    }
