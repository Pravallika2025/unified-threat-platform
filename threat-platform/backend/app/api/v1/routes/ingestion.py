from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.ingestion.application.ingest_service import IngestService
from app.modules.ingestion.application.upload_service import UploadService
from app.modules.ingestion.schemas import IngestRequest, IngestResponse
from app.modules.normalization.application.normalizer_service import NormalizerService

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/ingestion", tags=["ingestion"])


@router.post("/events", response_model=IngestResponse)
async def ingest_events(
    data: IngestRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission(Permission.DATA_UPLOAD)),
):
    result = await IngestService(db).ingest(
        environment_id=data.environment_id,
        source_type=data.source_type,
        records=data.records,
        uploaded_by=user.id,
    )
    return IngestResponse(**result.__dict__)


@router.post("/upload", response_model=IngestResponse)
async def upload_log_file(
    environment_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission(Permission.DATA_UPLOAD)),
):
    content = await file.read()
    result = await UploadService(db).handle_upload(
        environment_id=environment_id,
        filename=file.filename or "upload.log",
        content=content,
        uploaded_by=user.id,
    )
    return IngestResponse(**result.__dict__)


@router.post("/normalize")
async def normalize_pending(
    limit: int = 500,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.DATA_UPLOAD)),
):
    """Stage 2 on demand. In production the worker runs this on a schedule."""
    return {"normalized": await NormalizerService(db).process_pending(limit)}
