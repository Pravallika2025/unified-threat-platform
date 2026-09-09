"""Collector contract. Add a new data source by subclassing this — nothing else changes."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from app.modules.ingestion.domain.source_type import SourceType


class BaseCollector(ABC):
    source_type: SourceType

    @abstractmethod
    async def collect(self, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        """Yield raw records exactly as the source produced them. Do not transform here —
        normalization is a separate stage."""
        raise NotImplementedError

    def describe(self) -> dict[str, str]:
        return {"source_type": str(self.source_type), "collector": type(self).__name__}
