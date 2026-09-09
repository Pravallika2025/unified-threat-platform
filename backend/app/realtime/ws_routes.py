import asyncio
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.exceptions import AuthenticationError
from app.core.security.jwt import decode_token
from app.realtime.connection_manager import manager

logger = logging.getLogger(__name__)
router = APIRouter()

HEARTBEAT_SECONDS = 25


@router.websocket("/ws/live")
async def live_feed(websocket: WebSocket, token: str = Query(...)):
    """Browsers cannot set headers on a WebSocket handshake, so the access token
    arrives as a query parameter. It is still verified the same way."""
    try:
        payload = decode_token(token)
    except AuthenticationError:
        await websocket.close(code=4401, reason="Invalid or expired token")
        return

    connection = await manager.connect(
        websocket, user_id=payload["sub"], environment_id=payload.get("env")
    )
    await websocket.send_json({"type": "connected", "event": "ready", "data": {}})

    try:
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=HEARTBEAT_SECONDS)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "heartbeat", "event": "ping", "data": {}})
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(connection)
