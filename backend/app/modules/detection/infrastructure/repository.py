from __future__ import annotations

from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.detection.infrastructure.models import AlertModel
from app.shared.types import utcnow


class AlertRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, alert: AlertModel) -> AlertModel:
        self.db.add(alert)
        await self.db.flush()
        return alert

    async def get(self, alert_id: str) -> AlertModel | None:
        return await self.db.get(AlertModel, alert_id)

    async def list(
        self,
        *,
        environment_id: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[AlertModel]:
        stmt = select(AlertModel).order_by(AlertModel.created_at.desc()).limit(limit)
        if environment_id:
            stmt = stmt.where(AlertModel.environment_id == environment_id)
        if severity:
            stmt = stmt.where(AlertModel.severity == severity)
        if status:
            stmt = stmt.where(AlertModel.status == status)
        return list((await self.db.execute(stmt)).scalars())

    async def exists_recent(self, *, rule_id: str, entity: str, minutes: int) -> bool:
        cutoff = utcnow() - timedelta(minutes=minutes)
        stmt = select(func.count(AlertModel.id)).where(
            AlertModel.rule_id == rule_id,
            AlertModel.entity == entity,
            AlertModel.created_at >= cutoff,
        )
        return int((await self.db.execute(stmt)).scalar_one()) > 0

    async def count(self, *, since=None, severity: str | None = None) -> int:
        stmt = select(func.count(AlertModel.id))
        if since:
            stmt = stmt.where(AlertModel.created_at >= since)
        if severity:
            stmt = stmt.where(AlertModel.severity == severity)
        return int((await self.db.execute(stmt)).scalar_one())

    async def count_by_severity(self) -> dict[str, int]:
        stmt = select(AlertModel.severity, func.count(AlertModel.id)).group_by(AlertModel.severity)
        return {row[0]: row[1] for row in (await self.db.execute(stmt)).all()}

    async def count_by_rule(self, limit: int = 5) -> list[tuple[str, int]]:
        stmt = (
            select(AlertModel.rule_id, func.count(AlertModel.id).label("n"))
            .group_by(AlertModel.rule_id)
            .order_by(func.count(AlertModel.id).desc())
            .limit(limit)
        )
        return [(row[0], row[1]) for row in (await self.db.execute(stmt)).all()]

    async def top_entities(self, limit: int = 5) -> list[tuple[str, int, str]]:
        stmt = (
            select(
                AlertModel.entity,
                func.count(AlertModel.id).label("n"),
                func.max(AlertModel.severity),
            )
            .group_by(AlertModel.entity)
            .order_by(func.count(AlertModel.id).desc())
            .limit(limit)
        )
        return [(r[0], r[1], r[2]) for r in (await self.db.execute(stmt)).all()]
