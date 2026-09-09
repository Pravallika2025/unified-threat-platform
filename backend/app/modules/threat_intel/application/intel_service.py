from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.threat_intel.infrastructure.models import IndicatorModel
from app.modules.threat_intel.infrastructure.repository import IndicatorRepository


class IntelService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IndicatorRepository(db)

    async def list(self) -> list[IndicatorModel]:
        return await self.repo.all()

    async def add(self, indicators: list[IndicatorModel]) -> int:
        await self.repo.add_many(indicators)
        return len(indicators)
