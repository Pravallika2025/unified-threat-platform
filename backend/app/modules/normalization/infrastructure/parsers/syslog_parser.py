import re
from typing import Any

from app.modules.normalization.infrastructure.parsers.base_parser import BaseParser

KV_PATTERN = re.compile(r"(\w+)=([^\s\"]+|\"[^\"]*\")")
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
USER_PATTERN = re.compile(r"(?:user|for user|account)[\s:=]+([\w.\-@\\]+)", re.IGNORECASE)


class SyslogParser(BaseParser):
    """Best-effort extraction from unstructured log lines: key=value pairs, then regex."""

    def can_parse(self, record: dict[str, Any]) -> bool:
        return isinstance(record.get("raw"), str)

    def parse(self, record: dict[str, Any]) -> dict[str, Any]:
        line: str = record["raw"]
        from app.modules.normalization.domain.field_map import canonical_key

        out: dict[str, Any] = {"message": line}

        for key, value in KV_PATTERN.findall(line):
            out[canonical_key(key)] = value.strip('"')

        ips = IP_PATTERN.findall(line)
        if ips:
            out.setdefault("source_ip", ips[0])
            if len(ips) > 1:
                out.setdefault("destination_ip", ips[1])

        if match := USER_PATTERN.search(line):
            out.setdefault("user_name", match.group(1))

        lowered = line.lower()
        if "failed password" in lowered or "authentication failure" in lowered:
            out.setdefault("event_action", "login_failed")
            out.setdefault("event_outcome", "failure")
            out.setdefault("event_category", "authentication")
        elif "accepted password" in lowered or "session opened" in lowered:
            out.setdefault("event_action", "login_success")
            out.setdefault("event_outcome", "success")
            out.setdefault("event_category", "authentication")

        return out
