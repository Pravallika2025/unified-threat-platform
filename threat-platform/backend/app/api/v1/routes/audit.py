from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWorkRoute
from app.core.database import get_db
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.audit.application.audit_service import AuditService
from app.modules.audit.application.integrity_service import IntegrityService
from app.modules.audit.schemas import AuditEntryOut, ChainVerification

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditEntryOut])
async def list_audit(
    actor_id: str | None = None,
    resource_type: str | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.AUDIT_VIEW)),
):
    return await AuditService(db).list(
        actor_id=actor_id, resource_type=resource_type, limit=limit
    )


@router.get("/verify", response_model=ChainVerification)
async def verify_chain(
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_permission(Permission.AUDIT_VIEW)),
):
    """Walks the whole chain. If this returns valid=false, the log was tampered with."""
    return await IntegrityService(db).verify_chain()
