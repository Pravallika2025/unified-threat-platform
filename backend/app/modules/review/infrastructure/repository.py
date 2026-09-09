from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.review.infrastructure.models import DecisionModel


class DecisionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, decision: DecisionModel) -> DecisionModel:
        self.db.add(decision)
        await self.db.flush()
        return decision

    async def get(self, decision_id: str) -> DecisionModel | None:
        return await self.db.get(DecisionModel, decision_id)

    async def for_incident(self, incident_id: str) -> list[DecisionModel]:
        stmt = (
            select(DecisionModel)
            .where(DecisionModel.incident_id == incident_id)
            .order_by(DecisionModel.created_at.desc())
        )
        return list((await self.db.execute(stmt)).scalars())

    async def pending_approval(self) -> list[DecisionModel]:
        stmt = select(DecisionModel).where(
            DecisionModel.requires_approval.is_(True),
            DecisionModel.approved_by.is_(None),
        )
        return list((await self.db.execute(stmt)).scalars())
