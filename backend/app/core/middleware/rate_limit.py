"""In-memory sliding-window limiter.

Pure ASGI for the same reason as RequestIdMiddleware — see the note there.
Swap the counter for Redis in multi-instance deployments; this one is per-process.
"""

import time
from collections import defaultdict, deque

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class RateLimitMiddleware:
    def __init__(self, app: ASGIApp, *, limit: int = 300, window_seconds: int = 60):
        self.app = app
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        key = client[0] if client else "unknown"
        now = time.time()

        hits = self._hits[key]
        while hits and now - hits[0] > self.window:
            hits.popleft()

        if len(hits) >= self.limit:
            response = JSONResponse(
                status_code=429,
                content={"type": "rate_limited", "title": "Too many requests", "status": 429},
            )
            await response(scope, receive, send)
            return

        hits.append(now)
        await self.app(scope, receive, send)
