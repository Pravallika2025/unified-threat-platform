"""Exact-match IOC detection: file hashes, known-bad IPs, malicious URLs."""

import logging
from typing import Any

from app.modules.detection.domain.entities import Finding, Severity

logger = logging.getLogger(__name__)


class SignatureEngine:
    def __init__(self, ioc_index: dict[str, dict] | None = None):
        # {indicator_value: {"type": "ip"|"hash"|"url", "source": ..., "severity": ...}}
        self.ioc_index = ioc_index or {}

    def evaluate(self, events: list[Any]) -> list[Finding]:
        if not self.ioc_index:
            return []

        findings: list[Finding] = []
        for event in events:
            for value in (event.source_ip, event.destination_ip, event.file_hash, event.url):
                if not value:
                    continue
                ioc = self.ioc_index.get(str(value).lower())
                if not ioc:
                    continue
                findings.append(
                    Finding(
                        rule_id=f"IOC-{ioc.get('type', 'unknown').upper()}",
                        title=f"Known malicious {ioc.get('type')} observed: {value}",
                        severity=Severity(ioc.get("severity", "high")),
                        environment_id=event.environment_id,
                        event_ids=[event.id],
                        entity=str(value),
                        evidence={"indicator": value, "intel_source": ioc.get("source")},
                        attack=ioc.get("attack", {}),
                    )
                )
        return findings
