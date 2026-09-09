"""Configurable Regex log pattern parser."""

import re
from typing import Any

from app.modules.normalization.domain.field_map import canonical_key
from app.modules.normalization.infrastructure.parsers.base_parser import BaseParser

COMMON_REGEX_PATTERNS = [
    re.compile(r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(?P<host_name>[\w.-]+)\s+(?P<process_name>[\w.-]+)(?:\[(?P<pid>\d+)\])?:\s+(?P<message>.*)$"),
    re.compile(r"^(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+(?P<host_name>[\w.-]+)\s+(?P<process_name>[\w.-]+)(?:\[(?P<pid>\d+)\])?:\s+(?P<message>.*)$"),
]


class RegexParser(BaseParser):
    def __init__(self, patterns: list[re.Pattern] | None = None):
        self.patterns = patterns or COMMON_REGEX_PATTERNS

    def can_parse(self, record: dict[str, Any]) -> bool:
        raw = record.get("raw")
        return isinstance(raw, str) and not ("CEF:" in raw or "LEEF:" in raw)

    def parse(self, record: dict[str, Any]) -> dict[str, Any]:
        raw = record["raw"]
        out: dict[str, Any] = {"message": raw}

        for pattern in self.patterns:
            match = pattern.match(raw)
            if match:
                for key, val in match.groupdict().items():
                    if val is not None:
                        out[canonical_key(key)] = val
                break

        return out
