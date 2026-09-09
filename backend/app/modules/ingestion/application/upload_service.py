from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.modules.ingestion.application.ingest_service import IngestService
from app.modules.ingestion.domain.entities import IngestResult
from app.modules.ingestion.domain.source_type import SourceType
from app.modules.ingestion.infrastructure.collectors.file_upload_collector import (
    FileUploadCollector,
)

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_SUFFIXES = (".json", ".jsonl", ".ndjson", ".csv", ".log", ".txt")


class UploadService:
    def __init__(self, db: AsyncSession):
        self.ingest = IngestService(db)
        self.collector = FileUploadCollector()

    async def handle_upload(
        self, *, environment_id: str, filename: str, content: bytes, uploaded_by: str
    ) -> IngestResult:
        if len(content) > MAX_UPLOAD_BYTES:
            raise ValidationError("File exceeds the 25 MB upload limit")
        if not filename.lower().endswith(ALLOWED_SUFFIXES):
            raise ValidationError(f"Unsupported file type. Allowed: {', '.join(ALLOWED_SUFFIXES)}")

        records = [r async for r in self.collector.collect(content=content, filename=filename)]
        if not records:
            raise ValidationError("No parseable records found in the file")

        return await self.ingest.ingest(
            environment_id=environment_id,
            source_type=SourceType.USER_UPLOAD,
            records=records,
            uploaded_by=uploaded_by,
        )
