import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ingestion.infrastructure.repository import RawEventRepository
from app.modules.normalization.domain.field_map import canonical_outcome
from app.modules.normalization.infrastructure.models import NormalizedEventModel
from app.modules.normalization.infrastructure.parsers.base_parser import BaseParser
from app.modules.normalization.infrastructure.parsers.json_parser import JsonParser
from app.modules.normalization.infrastructure.parsers.syslog_parser import SyslogParser
from app.modules.normalization.infrastructure.repository import NormalizedEventRepository

logger = logging.getLogger(__name__)

CANONICAL_FIELDS = {
    "event_action", "event_outcome", "event_category", "source_ip", "destination_ip",
    "destination_port", "protocol", "user_name", "host_name", "process_name",
    "file_hash", "url", "bytes_out", "message",
}


class NormalizerService:
    """Stage 2 of the pipeline: raw records -> canonical NormalizedEvent rows."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.raw_repo = RawEventRepository(db)
        self.repo = NormalizedEventRepository(db)
        self.parsers: list[BaseParser] = [SyslogParser(), JsonParser()]

    async def process_pending(self, limit: int = 500) -> int:
        raw_events = await self.raw_repo.list_unprocessed(limit)
        if not raw_events:
            return 0

        normalized: list[NormalizedEventModel] = []
        processed_ids: list[str] = []

        for raw in raw_events:
            try:
                normalized.append(self._normalize_one(raw))
                processed_ids.append(raw.id)
            except Exception:
                logger.exception("Failed to normalize raw event %s", raw.id)
                processed_ids.append(raw.id)  # don't retry forever on a poison record

        await self.repo.add_many(normalized)
        await self.raw_repo.mark_processed(processed_ids)
        logger.info("Normalized %d events", len(normalized))
        return len(normalized)

    def _normalize_one(self, raw) -> NormalizedEventModel:
        parsed = self._parse(raw.payload)

        known = {k: v for k, v in parsed.items() if k in CANONICAL_FIELDS}
        extra = {k: v for k, v in parsed.items() if k not in CANONICAL_FIELDS and k != "timestamp"}

        return NormalizedEventModel(
            raw_event_id=raw.id,
            environment_id=raw.environment_id,
            source_type=raw.source_type,
            timestamp=self._parse_timestamp(parsed.get("timestamp")) or raw.received_at,
            event_action=_as_str(known.get("event_action")),
            event_outcome=canonical_outcome(known.get("event_outcome")),
            event_category=_as_str(known.get("event_category")),
            source_ip=_as_str(known.get("source_ip")),
            destination_ip=_as_str(known.get("destination_ip")),
            destination_port=_as_int(known.get("destination_port")),
            protocol=_as_str(known.get("protocol")),
            user_name=_as_str(known.get("user_name")),
            host_name=_as_str(known.get("host_name")),
            process_name=_as_str(known.get("process_name")),
            file_hash=_as_str(known.get("file_hash")),
            url=_as_str(known.get("url")),
            bytes_out=_as_int(known.get("bytes_out")),
            message=_as_str(known.get("message"), max_len=4000),
            extra=extra,
        )

    def _parse(self, payload: dict[str, Any]) -> dict[str, Any]:
        for parser in self.parsers:
            if parser.can_parse(payload):
                return parser.parse(payload)
        return {"message": str(payload)}

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            return None


def _as_str(value: Any, max_len: int = 255) -> str | None:
    if value is None:
        return None
    return str(value)[:max_len]


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
