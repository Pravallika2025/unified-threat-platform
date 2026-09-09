from abc import ABC, abstractmethod

from app.modules.threat_intel.domain.entities import Indicator


class BaseFeed(ABC):
    name: str

    @abstractmethod
    async def fetch(self) -> list[Indicator]:
        """Return indicators. Must be idempotent — callers de-duplicate by value+source."""
        raise NotImplementedError
