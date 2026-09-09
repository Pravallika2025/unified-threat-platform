from typing import Any

from app.modules.normalization.domain.field_map import canonical_key
from app.modules.normalization.infrastructure.parsers.base_parser import BaseParser


class JsonParser(BaseParser):
    """Structured records that already have named fields. Flattens one level of nesting."""

    def can_parse(self, record: dict[str, Any]) -> bool:
        return "raw" not in record

    def parse(self, record: dict[str, Any]) -> dict[str, Any]:
        flat: dict[str, Any] = {}
        for key, value in record.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat[canonical_key(f"{key}_{sub_key}")] = sub_value
                    flat.setdefault(canonical_key(sub_key), sub_value)
            else:
                flat[canonical_key(key)] = value
        return flat
