"""Custom threat intelligence feed loader.

Accepts internal IOC lists, curated CSVs, and domain blocklists.
"""

from app.modules.threat_intel.domain.entities import Indicator, IndicatorType
from app.modules.threat_intel.infrastructure.feeds.base_feed import BaseFeed

CUSTOM_IOCS = [
    ("phishing-alert@secure-bank-verify.com", IndicatorType.EMAIL, 90, "high", "Spearphishing sender address"),
    ("malicious-update-server.xyz", IndicatorType.DOMAIN, 85, "high", "Fake software update server"),
    ("192.0.2.144", IndicatorType.IP, 75, "medium", "Compromised proxy relay"),
]


class CustomFeed(BaseFeed):
    name = "Custom Internal Feed"

    def __init__(self, raw_indicators: list[dict] | None = None):
        self.raw_indicators = raw_indicators or []

    async def fetch(self) -> list[Indicator]:
        indicators: list[Indicator] = []
        for val, itype, confidence, severity, desc in CUSTOM_IOCS:
            indicators.append(
                Indicator(
                    value=val.lower().strip(),
                    type=itype,
                    source=self.name,
                    confidence=confidence,
                    severity=severity,
                    description=desc,
                )
            )

        for item in self.raw_indicators:
            val = item.get("value")
            if val:
                itype = item.get("type", "ip")
                try:
                    ind_type = IndicatorType(itype)
                except ValueError:
                    ind_type = IndicatorType.IP

                indicators.append(
                    Indicator(
                        value=str(val).lower().strip(),
                        type=ind_type,
                        source=item.get("source", self.name),
                        confidence=int(item.get("confidence", 80)),
                        severity=str(item.get("severity", "high")),
                        description=str(item.get("description", "Custom IOC")),
                    )
                )

        return indicators
