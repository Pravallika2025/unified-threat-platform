"""Maps findings to MITRE ATT&CK tactics/techniques for reporting."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.threat_intel.infrastructure.repository import AttackTechniqueRepository


class AttackMapper:
    def __init__(self, db: AsyncSession):
        self.repo = AttackTechniqueRepository(db)

    async def describe(self, technique_id: str | None) -> dict | None:
        if not technique_id:
            return None
        technique = await self.repo.get(technique_id)
        if technique is None:
            return {"technique": technique_id, "name": "Unknown technique"}
        return {
            "technique": technique.id,
            "name": technique.name,
            "tactic": technique.tactic,
            "tactic_name": technique.tactic_name,
        }
