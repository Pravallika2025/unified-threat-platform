from collections.abc import AsyncIterator
from typing import Any

from app.modules.ingestion.domain.source_type import SourceType
from app.modules.ingestion.infrastructure.collectors.base import BaseCollector


class SyslogCollector(BaseCollector):
    """Accepts syslog lines pushed over HTTP.

    TODO: add a UDP/TCP listener (asyncio.start_server on 514) for push-mode sources.
    """

    source_type = SourceType.FIREWALL

    async def collect(self, *, lines: list[str], **_: Any) -> AsyncIterator[dict]:
        for line in lines:
            if line.strip():
                yield {"raw": line}
