"""MITRE ATT&CK threat intelligence feed provider.

Supplies standard ATT&CK technique indicators, hashes, and behavioral IOC patterns.
"""

from app.modules.threat_intel.domain.entities import Indicator, IndicatorType
from app.modules.threat_intel.infrastructure.feeds.base_feed import BaseFeed

MITRE_INDICATORS = [
    # Known malware hashes associated with ATT&CK groups
    ("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", IndicatorType.HASH, 90, "high", "T1059 - Command and Scripting Interpreter Test Hash"),
    ("44d88612fea8a8f36de82e1278abb02f", IndicatorType.HASH, 95, "critical", "T1204 - EICAR / Malicious payload reference"),
    ("275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f", IndicatorType.HASH, 95, "critical", "T1486 - Mimikatz LSASS dumper signature"),
    ("c0202cf6aeab8437a602b78b13d2d43529da134d", IndicatorType.HASH, 90, "high", "T1021 - PsExec / Remote execution utility hash"),
    # Malicious domains / C2 endpoints
    ("c2.evil-corp.internal", IndicatorType.DOMAIN, 90, "critical", "T1071 - Application Layer C2 Domain"),
    ("exfil.darkside-ransomware.net", IndicatorType.DOMAIN, 95, "critical", "T1048 - Exfiltration Destination"),
    ("pastebin.com/raw/malware", IndicatorType.URL, 80, "medium", "T1102 - Web Service Hosted Payload"),
]


class MitreAttackFeed(BaseFeed):
    name = "MITRE ATT&CK"

    async def fetch(self) -> list[Indicator]:
        indicators: list[Indicator] = []
        for val, itype, confidence, severity, desc in MITRE_INDICATORS:
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
        return indicators
