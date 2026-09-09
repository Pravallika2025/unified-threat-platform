from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.domain.entities import GENESIS_HASH
from app.modules.audit.infrastructure.models import AuditEntryModel
from app.modules.audit.infrastructure.repository import AuditRepository
from app.shared.types import utcnow
from app.shared.utils.hashing import canonical_json, canonical_timestamp, sha256_hex

logger = logging.getLogger(__name__)


def compute_entry_hash(
    *,
    prev_hash: str,
    actor_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str | None,
    details: dict,
    created_at,
) -> str:
    """Each entry commits to its predecessor. Altering any past row breaks every hash after it."""
    return sha256_hex(
        canonical_json(
            {
                "prev": prev_hash,
                "actor": actor_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details,
                "at": canonical_timestamp(created_at),
            }
        )
    )


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AuditRepository(db)

    async def record(
        self,
        *,
        actor_id: str | None,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        details: dict | None = None,
    ) -> AuditEntryModel:
        details = details or {}
        previous = await self.repo.latest()
        prev_hash = previous.entry_hash if previous else GENESIS_HASH
        created_at = utcnow()

        entry = AuditEntryModel(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            prev_hash=prev_hash,
            entry_hash=compute_entry_hash(
                prev_hash=prev_hash,
                actor_id=actor_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                created_at=created_at,
            ),
            created_at=created_at,
        )
        return await self.repo.add(entry)

    async def list(self, **filters) -> list[AuditEntryModel]:
        return await self.repo.list(**filters)
