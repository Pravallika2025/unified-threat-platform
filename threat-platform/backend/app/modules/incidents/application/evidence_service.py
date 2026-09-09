from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.infrastructure.models import EvidenceModel
from app.modules.incidents.infrastructure.repository import EvidenceRepository
from app.shared.utils.hashing import canonical_json, sha256_hex


class EvidenceService:
    """Evidence is written once and hashed. There is no update or delete path — by design."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EvidenceRepository(db)

    async def attach(
        self, *, incident_id: str, kind: str, content: dict, collected_by: str | None
    ) -> EvidenceModel:
        return await self.repo.add(
            EvidenceModel(
                incident_id=incident_id,
                kind=kind,
                content=content,
                content_hash=sha256_hex(canonical_json(content)),
                collected_by=collected_by,
            )
        )

    async def list(self, incident_id: str) -> list[EvidenceModel]:
        return await self.repo.for_incident(incident_id)

    async def verify(self, incident_id: str) -> list[dict]:
        """Recompute each hash and report any evidence that no longer matches."""
        results = []
        for item in await self.repo.for_incident(incident_id):
            expected = sha256_hex(canonical_json(item.content))
            results.append(
                {
                    "evidence_id": item.id,
                    "kind": item.kind,
                    "intact": expected == item.content_hash,
                }
            )
        return results
