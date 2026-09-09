"""One transaction per request, committed before the response is sent.

FastAPI closes dependency generators *after* the response has been handed to the
client, so committing in `get_db`'s teardown means a caller can receive 200 OK and
immediately issue a follow-up request that does not yet see the write. That is not
a theoretical race — it broke the ingest -> normalize -> detect chain, where each
step depends on the previous one having landed.

This route class runs the endpoint, writes the audit entry, and commits, all before
returning the response object. The audit entry is therefore atomic with the change
it describes: if the commit fails, neither exists.
"""

import logging
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request, Response
from fastapi.routing import APIRoute

logger = logging.getLogger(__name__)

AUDITED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
# Login and refresh are audited by AuthService itself, which knows the outcome.
AUDIT_SKIP_PATHS = {"/api/v1/auth/login", "/api/v1/auth/refresh"}


class UnitOfWorkRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_handler = super().get_route_handler()

        async def unit_of_work_handler(request: Request) -> Response:
            response = await original_handler(request)

            session = getattr(request.state, "db", None)
            if session is None:
                return response

            try:
                await self._audit(request, response, session)
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Failed to commit unit of work for %s", request.url.path)
                raise

            return response

        return unit_of_work_handler

    @staticmethod
    async def _audit(request: Request, response: Response, session) -> None:
        if request.method not in AUDITED_METHODS:
            return
        if request.url.path in AUDIT_SKIP_PATHS:
            return
        if response.status_code >= 400:
            return

        from app.modules.audit.application.audit_service import AuditService

        await AuditService(session).record(
            actor_id=getattr(request.state, "user_id", None),
            action=f"{request.method} {request.url.path}",
            resource_type="http_request",
            resource_id=None,
            details={
                "status": response.status_code,
                "request_id": getattr(request.state, "request_id", None),
                "client": request.client.host if request.client else None,
            },
        )
