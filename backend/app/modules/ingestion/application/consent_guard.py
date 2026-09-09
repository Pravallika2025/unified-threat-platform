"""Charter principle 1: only authorized / permitted data sources.

Every ingest call passes through here. An environment declares which source types
it has authorised; anything else is rejected and the rejection is auditable.
"""

from app.core.exceptions import PermissionDeniedError
from app.modules.ingestion.domain.source_type import SourceType


class ConsentGuard:
    def __init__(self, authorized_sources: list[str]):
        self.authorized = set(authorized_sources or [])

    def is_allowed(self, source_type: SourceType | str) -> bool:
        if "all" in self.authorized:
            return True
        return str(source_type) in self.authorized

    def assert_allowed(self, source_type: SourceType | str, environment_name: str) -> None:
        if not self.is_allowed(source_type):
            raise PermissionDeniedError(
                f"Source '{source_type}' is not authorized for environment "
                f"'{environment_name}'. Add it to the environment's authorized sources first.",
                details={"source_type": str(source_type)},
            )
