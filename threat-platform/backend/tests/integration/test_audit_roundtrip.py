"""Regression: the audit chain must verify after a database round trip.

This caught a real bug — SQLite drops tzinfo on read, so hashing the raw datetime
produced a different value on verification than on write, and every chain check
failed. canonical_timestamp() normalises both sides.
"""

import os

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_audit.db")

from sqlalchemy import select  # noqa: E402

from app.core.database import SessionLocal, create_all  # noqa: E402
from app.modules.audit.application.audit_service import AuditService  # noqa: E402
from app.modules.audit.application.integrity_service import IntegrityService  # noqa: E402
from app.modules.audit.infrastructure.models import AuditEntryModel  # noqa: E402


@pytest.mark.asyncio
async def test_chain_verifies_after_round_trip():
    await create_all()
    async with SessionLocal() as db:
        for i in range(3):
            await AuditService(db).record(
                actor_id="user-1", action=f"action.{i}", resource_type="test"
            )
        await db.commit()

    async with SessionLocal() as db:
        result = await IntegrityService(db).verify_chain()

    assert result["valid"] is True
    assert result["checked"] >= 3


@pytest.mark.asyncio
async def test_tampering_is_detected():
    await create_all()
    async with SessionLocal() as db:
        entry = await AuditService(db).record(
            actor_id="user-1", action="sensitive.action", resource_type="incident"
        )
        await db.commit()
        target_sequence = entry.sequence

    # Simulate someone editing the log directly in the database.
    async with SessionLocal() as db:
        row = (
            await db.execute(
                select(AuditEntryModel).where(AuditEntryModel.sequence == target_sequence)
            )
        ).scalar_one()
        row.details = {"tampered": True}
        await db.commit()

    async with SessionLocal() as db:
        result = await IntegrityService(db).verify_chain()

    assert result["valid"] is False
    assert result["broken_at"] is not None
