from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.unit_of_work import UnitOfWorkRoute
from app.core.security.dependencies import CurrentUser, require_permission
from app.core.security.permissions import Permission
from app.modules.notifications.application.notification_service import notification_service

router = APIRouter(route_class=UnitOfWorkRoute, prefix="/notifications", tags=["notifications"])


class SmtpConfigIn(BaseModel):
    smtp_host: str = Field(..., description="SMTP server hostname e.g. smtp.gmail.com")
    smtp_port: int = Field(587, description="SMTP server port e.g. 587")
    smtp_user: str = Field(..., description="SMTP account username or email")
    smtp_password: str = Field(..., description="SMTP account password or app password")
    from_addr: str = Field("alerts@threatplatform.dev", description="Sender email address")
    to_addr: str = Field("soc-team@threatplatform.dev", description="Default alert recipient")


class SmtpTestIn(BaseModel):
    to_addr: str | None = Field(None, description="Optional target email address for test dispatch")


@router.get("/smtp")
async def get_smtp_config(
    _: CurrentUser = Depends(require_permission(Permission.ALERT_VIEW)),
):
    """Retrieve safe SMTP status and configuration parameters."""
    channel = notification_service.get_email_channel()
    if not channel:
        return {"is_configured": False, "is_mock_mode": True}
    return channel.get_config()


@router.post("/smtp")
async def update_smtp_config(
    data: SmtpConfigIn,
    _: CurrentUser = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    """Update runtime SMTP credentials for real-time email dispatch."""
    channel = notification_service.get_email_channel()
    if not channel:
        return {"error": "Email channel not active"}
    updated = channel.update_credentials(
        smtp_host=data.smtp_host,
        smtp_port=data.smtp_port,
        smtp_user=data.smtp_user,
        smtp_password=data.smtp_password,
        from_addr=data.from_addr,
        to_addr=data.to_addr,
    )
    return {"status": "success", "config": updated}


@router.post("/smtp/test")
async def test_smtp_alert(
    data: SmtpTestIn | None = None,
    _: CurrentUser = Depends(require_permission(Permission.ALERT_VIEW)),
):
    """Dispatch an immediate test alert to verify real email delivery."""
    channel = notification_service.get_email_channel()
    if not channel:
        return {"success": False, "message": "Email channel unavailable"}
    target = data.to_addr if data else None
    return await channel.send_test_email(target_to=target)
