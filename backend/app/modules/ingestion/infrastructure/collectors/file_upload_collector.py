import csv
import io
import json
from collections.abc import AsyncIterator
from typing import Any

from app.modules.ingestion.domain.source_type import SourceType
from app.modules.ingestion.infrastructure.collectors.base import BaseCollector


class FileUploadCollector(BaseCollector):
    """Handles user-uploaded log files: .json, .jsonl, .csv, or plain syslog lines."""

    source_type = SourceType.USER_UPLOAD

    async def collect(self, *, content: bytes, filename: str, **_: Any) -> AsyncIterator[dict]:
        text = content.decode("utf-8", errors="replace")
        name = filename.lower()

        if name.endswith(".json"):
            data = json.loads(text)
            records = data if isinstance(data, list) else [data]
            for record in records:
                yield record

        elif name.endswith(".jsonl") or name.endswith(".ndjson"):
            for line in text.splitlines():
                if line.strip():
                    yield json.loads(line)

        elif name.endswith(".csv"):
            for row in csv.DictReader(io.StringIO(text)):
                yield dict(row)

        else:  # treat as raw log lines
            for line in text.splitlines():
                if line.strip():
                    yield {"raw": line, "source_file": filename}
