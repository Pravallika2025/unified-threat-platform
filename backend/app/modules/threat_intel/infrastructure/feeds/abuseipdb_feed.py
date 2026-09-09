"""AbuseIPDB threat intelligence feed provider.

Pulls malicious IP addresses and reputation scores.
Supports offline curated feed data with live API fallback if configured.
"""

import logging
import os
from typing import Any

from app.modules.threat_intel.domain.entities import Indicator, IndicatorType
from app.modules.threat_intel.infrastructure.feeds.base_feed import BaseFeed

logger = logging.getLogger(__name__)

CURATED_ABUSE_IPS = [
    ("203.0.113.77", 95, "critical", "Known SSH brute-force botnet node"),
    ("198.51.100.23", 88, "high", "Active scanner / port sweeper"),
    ("185.220.101.5", 90, "high", "Tor exit node associated with credential stuffing"),
    ("45.154.255.89", 85, "high", "Known C2 infrastructure / Cobalt Strike beacon"),
    ("194.26.29.112", 92, "critical", "Ransomware distribution host"),
    ("91.240.118.172", 78, "medium", "Automated vulnerability scanner"),
    ("193.142.146.35", 82, "high", "Brute-force and dictionary attack origin"),
    ("103.151.125.10", 75, "medium", "Malicious proxy node"),
]


class AbuseIPDBFeed(BaseFeed):
    name = "AbuseIPDB"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("ABUSEIPDB_API_KEY")

    async def fetch(self) -> list[Indicator]:
        indicators: list[Indicator] = []

        # Always supply curated baseline feed indicators
        for ip, confidence, severity, desc in CURATED_ABUSE_IPS:
            indicators.append(
                Indicator(
                    value=ip.lower().strip(),
                    type=IndicatorType.IP,
                    source=self.name,
                    confidence=confidence,
                    severity=severity,
                    description=desc,
                )
            )

        if self.api_key:
            try:
                import httpx

                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(
                        "https://api.abuseipdb.com/api/v2/blacklist",
                        headers={"Key": self.api_key, "Accept": "application/json"},
                        params={"confidenceMinimum": 90, "limit": 100},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        for item in data.get("data", []):
                            ip = item.get("ipAddress")
                            score = item.get("abuseConfidenceScore", 80)
                            if ip:
                                indicators.append(
                                    Indicator(
                                        value=ip.lower().strip(),
                                        type=IndicatorType.IP,
                                        source=self.name,
                                        confidence=score,
                                        severity="critical" if score >= 90 else "high",
                                        description="AbuseIPDB live blacklist feed entry",
                                    )
                                )
            except Exception as exc:
                logger.warning("Live AbuseIPDB sync failed (using curated dataset): %s", exc)

        return indicators
