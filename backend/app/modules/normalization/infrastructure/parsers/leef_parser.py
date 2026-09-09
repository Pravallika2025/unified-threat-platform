"""IBM QRadar Log Event Extended Format (LEEF) parser.

LEEF format:
LEEF:Version|Vendor|Product|Version|EventID|[Delimiter]|Key=Value
"""

import re
from typing import Any

from app.modules.normalization.domain.field_map import canonical_key
from app.modules.normalization.infrastructure.parsers.base_parser import BaseParser

LEEF_EXT_KV = re.compile(r"(\w+)=([^\t\x00-\x1f\n]+)")


class LeefParser(BaseParser):
    def can_parse(self, record: dict[str, Any]) -> bool:
        raw = record.get("raw")
        return isinstance(raw, str) and ("LEEF:" in raw or raw.startswith("LEEF:"))

    def parse(self, record: dict[str, Any]) -> dict[str, Any]:
        raw = record["raw"]
        out: dict[str, Any] = {"message": raw}

        leef_idx = raw.find("LEEF:")
        leef_str = raw[leef_idx:] if leef_idx >= 0 else raw

        parts = leef_str.split("|")
        if len(parts) >= 5:
            out["vendor"] = parts[1]
            out["product"] = parts[2]
            out["event_action"] = parts[4]

            # Extension attributes
            ext_str = "|".join(parts[5:])
            for key, val in LEEF_EXT_KV.findall(ext_str):
                k = canonical_key(key)
                if k == "src":
                    out.setdefault("source_ip", val)
                elif k == "dst":
                    out.setdefault("destination_ip", val)
                elif k == "dstport":
                    try:
                        out.setdefault("destination_port", int(val))
                    except ValueError:
                        pass
                elif k in {"usrName", "username", "account"}:
                    out.setdefault("user_name", val)
                else:
                    out[k] = val

        return out
