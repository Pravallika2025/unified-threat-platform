"""Loads per-environment detection profiles from detection-content/environment-profiles.

A hospital and a school get different thresholds for the same rule — that difference
is data, not code.
"""

import logging
from functools import lru_cache
from pathlib import Path

import yaml

from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_PROFILE = {
    "risk_multiplier": 1.0,
    "enabled_rule_categories": ["all"],
    "critical_assets": [],
    "auto_response_allowed": False,
}


@lru_cache(maxsize=32)
def load_profile(environment_type: str) -> dict:
    path: Path = settings.detection_content_dir / "environment-profiles" / f"{environment_type}.yml"
    if not path.exists():
        logger.warning("No profile for environment type '%s', using defaults", environment_type)
        return dict(DEFAULT_PROFILE)
    with path.open() as fh:
        data = yaml.safe_load(fh) or {}
    return {**DEFAULT_PROFILE, **data}


def clear_profile_cache() -> None:
    load_profile.cache_clear()
