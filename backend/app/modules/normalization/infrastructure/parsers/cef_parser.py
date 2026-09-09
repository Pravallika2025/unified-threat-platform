"""ArcSight Common Event Format (CEF) log parser.

CEF format:
CEF:Version|Device Vendor|Device Product|Device Version|Device Event Class ID|Name|Severity|[Extension]
"""

import re
from typing import Any

from app.modules.normalization.domain.field_map import canonical_key
from app.modules.normalization.infrastructure.parsers.base_parser import BaseParser

CEF_EXT_KV = re.compile(r"(\w+)=([^\s=]+(?:\s+(?!\w+=)[^\s=]+)*)")


class CefParser(BaseParser):
    def can_parse(self, record: dict[str, Any]) -> bool:
        raw = record.get("raw")
        return isinstance(raw, str) and ("CEF:" in raw or raw.startswith("CEF:"))

    def parse(self, record: dict[str, Any]) -> dict[str, Any]:
        raw = record["raw"]
        out: dict[str, Any] = {"message": raw}

        # Find where CEF: starts
        cef_idx = raw.find("CEF:")
        cef_str = raw[cef_idx:] if cef_idx >= 0 else raw

        parts = cef_str.split("|")
        if len(parts) >= 8:
            out["vendor"] = parts[1]
            out["product"] = parts[2]
            out["event_action"] = parts[5]
            out["severity"] = parts[6]

            # Extension is in the 8th part onwards
            extension = "|".join(parts[7:])
            for key, val in CEF_EXT_KV.findall(extension):
                k = canonical_key(key)
                if k == "src":
                    out.setdefault("source_ip", val)
                elif k == "dst":
                    out.setdefault("destination_ip", val)
                elif k in {"dpt", "dst_port"}:
                    try:
                        out.setdefault("destination_port", int(val))
                    except ValueError:
                        pass
                elif k in {"suser", "duser", "user"}:
                    out.setdefault("user_name", val)
                elif k in {"shost", "dhost", "host"}:
                    out.setdefault("host_name", val)
                elif k == "out":
                    try:
                        out.setdefault("bytes_out", int(val))
                    except ValueError:
                        pass
                else:
                    out[k] = val

        return out
