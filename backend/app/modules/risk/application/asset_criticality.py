"""Assets an environment declares critical weight their incidents higher.

Defined per environment in detection-content/environment-profiles/<type>.yml.
"""

CRITICAL_WEIGHT = 1.4
NORMAL_WEIGHT = 1.0


def criticality_for(asset: str | None, critical_assets: list[str]) -> float:
    if not asset or not critical_assets:
        return NORMAL_WEIGHT
    asset_lower = str(asset).lower()
    for pattern in critical_assets:
        if str(pattern).lower() in asset_lower:
            return CRITICAL_WEIGHT
    return NORMAL_WEIGHT
