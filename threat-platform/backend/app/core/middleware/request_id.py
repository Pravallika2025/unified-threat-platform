"""Correlation ID for every request.

Written as pure ASGI middleware rather than Starlette's BaseHTTPMiddleware.
BaseHTTPMiddleware wraps the response in a stream, which defers FastAPI's
dependency teardown until after the body has been sent — meaning the database
session commits *after* the client already has its response. A client that
immediately issues a dependent request can then read stale data. Pure ASGI
middleware keeps teardown inside the request.
"""

import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send

HEADER = "x-request-id"


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = dict(scope.get("headers") or {})
        request_id = next(
            (v.decode() for k, v in (scope.get("headers") or []) if k == HEADER.encode()),
            None,
        ) or str(uuid.uuid4())

        scope.setdefault("state", {})["request_id"] = request_id

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                message["headers"].append((HEADER.encode(), request_id.encode()))
            await send(message)

        await self.app(scope, receive, send_with_header)
