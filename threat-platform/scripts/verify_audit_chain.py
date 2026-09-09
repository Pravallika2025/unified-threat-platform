#!/usr/bin/env python3
"""Verify the audit hash chain directly against the database, bypassing the API.

  cd backend && python ../scripts/verify_audit_chain.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.core.database import SessionLocal  # noqa: E402
from app.modules.audit.application.integrity_service import IntegrityService  # noqa: E402


async def main() -> int:
    async with SessionLocal() as db:
        result = await IntegrityService(db).verify_chain()

    if result["valid"]:
        print(f"Audit chain intact — {result['checked']} entries verified.")
        return 0

    print(f"CHAIN BROKEN at entry {result['broken_at']}: {result['reason']}")
    print(f"Entries checked before the break: {result['checked']}")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
