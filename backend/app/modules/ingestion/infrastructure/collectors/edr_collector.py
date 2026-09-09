"""EDR telemetry log collector."""

from collections.abc import AsyncIterator
from typing import Any

from app.modules.ingestion.domain.source_type import SourceType
from app.modules.ingestion.infrastructure.collectors.base import BaseCollector


class EdrCollector(BaseCollector):
    source_type = SourceType.EDR

    async def collect(self, records: list[dict[str, Any]] | None = None, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        for record in records or []:
            yield record
