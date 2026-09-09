from dataclasses import dataclass
from enum import StrEnum


class Verdict(StrEnum):
    MALICIOUS = "malicious"
    SUSPICIOUS = "suspicious"
    BENIGN = "benign"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class EngineVerdict:
    engine: str
    verdict: Verdict
    confidence: float  # 0.0 - 1.0
    rationale: str
