"""CSV / Tabular single-record log parser."""

import csv
import io
from typing import Any

from app.modules.normalization.domain.field_map import canonical_key
from app.modules.normalization.infrastructure.parsers.base_parser import BaseParser


class CsvParser(BaseParser):
    def can_parse(self, record: dict[str, Any]) -> bool:
        raw = record.get("raw")
        return isinstance(raw, str) and ("," in raw or "\t" in raw) and not ("CEF:" in raw or "LEEF:" in raw)

    def parse(self, record: dict[str, Any]) -> dict[str, Any]:
        raw = record["raw"]
        out: dict[str, Any] = {"message": raw}

        delimiter = "\t" if "\t" in raw and "," not in raw else ","
        try:
            reader = csv.reader(io.StringIO(raw), delimiter=delimiter)
            fields = next(reader, [])
            # Map positioned columns if headers or key-values
            for idx, col in enumerate(fields):
                if "=" in col:
                    k, v = col.split("=", 1)
                    out[canonical_key(k.strip())] = v.strip()
                else:
                    out[f"col_{idx}"] = col.strip()
        except Exception:
            pass

        return out
