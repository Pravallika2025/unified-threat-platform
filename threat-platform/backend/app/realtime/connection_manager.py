"""WebSocket fan-out for the live dashboard — section 13.

In-process registry. For multi-instance deployments, bridge through Redis pub/sub
(see event_bus.py) so every instance sees every message.
"""

import logging
from dataclasses import dataclass, field

from fastapi import WebSocket

logger = logging.getLogger(__name__)


@dataclass
class Connection:
    websocket: WebSocket
    user_id: str
    environment_id: str | None = None


@dataclass
class ConnectionManager:
    connections: list[Connection] = field(default_factory=list)

    async def connect(
        self, websocket: WebSocket, *, user_id: str, environment_id: str | None
    ) -> Connection:
        await websocket.accept()
        connection = Connection(websocket, user_id, environment_id)
        self.connections.append(connection)
        logger.info("WebSocket connected: user=%s (%d open)", user_id, len(self.connections))
        return connection

    def disconnect(self, connection: Connection) -> None:
        if connection in self.connections:
            self.connections.remove(connection)

    async def broadcast(self, message: dict, *, environment_id: str | None = None) -> None:
        """Send to everyone, or only to viewers of one environment."""
        dead: list[Connection] = []

        for connection in self.connections:
            # An environment-scoped user only receives their own environment's traffic.
            if connection.environment_id and environment_id:
                if connection.environment_id != environment_id:
                    continue
            try:
                await connection.websocket.send_json(message)
            except Exception:
                dead.append(connection)

        for connection in dead:
            self.disconnect(connection)

    @property
    def count(self) -> int:
        return len(self.connections)


manager = ConnectionManager()
