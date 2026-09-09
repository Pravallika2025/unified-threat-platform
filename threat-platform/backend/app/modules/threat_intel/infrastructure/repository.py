from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.threat_intel.infrastructure.models import AttackTechniqueModel, IndicatorModel


class IndicatorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def all(self) -> list[IndicatorModel]:
        return list((await self.db.execute(select(IndicatorModel))).scalars())

    async def add_many(self, indicators: list[IndicatorModel]) -> None:
        self.db.add_all(indicators)
        await self.db.flush()

    async def count(self) -> int:
        return int((await self.db.execute(select(func.count(IndicatorModel.id)))).scalar_one())


class AttackTechniqueRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, technique_id: str) -> AttackTechniqueModel | None:
        return await self.db.get(AttackTechniqueModel, technique_id)

    async def all(self) -> list[AttackTechniqueModel]:
        return list((await self.db.execute(select(AttackTechniqueModel))).scalars())
