from dataclasses import dataclass
from enum import StrEnum


class IndicatorType(StrEnum):
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    HASH = "hash"
    EMAIL = "email"


@dataclass
class Indicator:
    value: str
    type: IndicatorType
    source: str
    confidence: int      # 0-100
    severity: str
    description: str = ""
