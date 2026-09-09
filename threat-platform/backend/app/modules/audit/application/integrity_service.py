from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.application.audit_service import compute_entry_hash
from app.modules.audit.domain.entities import GENESIS_HASH
from app.modules.audit.infrastructure.repository import AuditRepository


class IntegrityService:
    """Walks the audit chain and reports the first entry that fails verification."""

    def __init__(self, db: AsyncSession):
        self.repo = AuditRepository(db)

    async def verify_chain(self) -> dict:
        entries = await self.repo.all_ordered()
        expected_prev = GENESIS_HASH

        for entry in entries:
            if entry.prev_hash != expected_prev:
                return {
                    "valid": False,
                    "checked": len(entries),
                    "broken_at": entry.id,
                    "reason": "Previous-hash link does not match",
                }

            recomputed = compute_entry_hash(
                prev_hash=entry.prev_hash,
                actor_id=entry.actor_id,
                action=entry.action,
                resource_type=entry.resource_type,
                resource_id=entry.resource_id,
                details=entry.details,
                created_at=entry.created_at,
            )
            if recomputed != entry.entry_hash:
                return {
                    "valid": False,
                    "checked": len(entries),
                    "broken_at": entry.id,
                    "reason": "Entry contents do not match its recorded hash",
                }
            expected_prev = entry.entry_hash

        return {"valid": True, "checked": len(entries), "broken_at": None, "reason": None}
