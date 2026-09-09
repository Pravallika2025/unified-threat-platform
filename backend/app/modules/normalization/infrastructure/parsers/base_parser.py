from abc import ABC, abstractmethod
from typing import Any


class BaseParser(ABC):
    """A parser turns one vendor's record into a flat dict of canonical keys."""

    @abstractmethod
    def can_parse(self, record: dict[str, Any]) -> bool: ...

    @abstractmethod
    def parse(self, record: dict[str, Any]) -> dict[str, Any]: ...
