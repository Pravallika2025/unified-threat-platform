"""Sample analyst account and a small threat-intel set, for development only.

Charter principle: no fake data or statistics. Nothing here fabricates metrics —
these are seed records you can act on, and this module refuses to run outside
development.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security.password import hash_password
from app.core.security.permissions import Role
from app.modules.environments.infrastructure.models import EnvironmentModel
from app.modules.environments.infrastructure.repository import EnvironmentRepository
from app.modules.iam.infrastructure.models import UserModel
from app.modules.iam.infrastructure.repository import UserRepository
from app.modules.threat_intel.infrastructure.models import (
    AttackTechniqueModel,
    IndicatorModel,
)
from app.modules.threat_intel.infrastructure.repository import IndicatorRepository
from app.seeds.environment_types import SEED_ENVIRONMENTS

logger = logging.getLogger(__name__)

ATTACK_TECHNIQUES = [
    ("T1110", "Brute Force", "TA0006", "Credential Access"),
    ("T1078", "Valid Accounts", "TA0001", "Initial Access"),
    ("T1021", "Remote Services", "TA0008", "Lateral Movement"),
    ("T1048", "Exfiltration Over Alternative Protocol", "TA0010", "Exfiltration"),
    ("T1059", "Command and Scripting Interpreter", "TA0002", "Execution"),
    ("T1071", "Application Layer Protocol", "TA0011", "Command and Control"),
    ("T1486", "Data Encrypted for Impact", "TA0040", "Impact"),
]

# Documentation-range addresses (RFC 5737) — safe placeholders, not real threats.
SAMPLE_INDICATORS = [
    ("203.0.113.77", "ip", "seed-example", 60, "high"),
    ("198.51.100.23", "ip", "seed-example", 55, "medium"),
]


async def seed_demo(db: AsyncSession) -> None:
    if not settings.is_dev:
        logger.warning("Refusing to seed demo data outside development")
        return

    env_repo = EnvironmentRepository(db)
    existing = {e.name for e in await env_repo.list()}
    created_envs = []
    for spec in SEED_ENVIRONMENTS:
        if spec["name"] in existing:
            continue
        created_envs.append(await env_repo.add(EnvironmentModel(**spec)))
    if created_envs:
        logger.info("Created %d environments", len(created_envs))

    user_repo = UserRepository(db)
    if not await user_repo.get_by_email("analyst@threatplatform.dev"):
        await user_repo.add(
            UserModel(
                email="analyst@threatplatform.dev",
                full_name="Sample Analyst",
                password_hash=hash_password("Analyst@12345"),
                role=str(Role.SECURITY_ANALYST),
            )
        )
        logger.info("Created sample analyst: analyst@threatplatform.dev / Analyst@12345")

    for technique_id, name, tactic, tactic_name in ATTACK_TECHNIQUES:
        if await db.get(AttackTechniqueModel, technique_id) is None:
            db.add(
                AttackTechniqueModel(
                    id=technique_id, name=name, tactic=tactic, tactic_name=tactic_name
                )
            )

    indicator_repo = IndicatorRepository(db)
    if await indicator_repo.count() == 0:
        await indicator_repo.add_many(
            [
                IndicatorModel(
                    value=value,
                    type=kind,
                    source=source,
                    confidence=confidence,
                    severity=severity,
                    description="Seed indicator (RFC 5737 documentation range)",
                )
                for value, kind, source, confidence, severity in SAMPLE_INDICATORS
            ]
        )

    await db.flush()
