from app.realtime.connection_manager import manager


class InAppChannel:
    """Pushes to every connected dashboard over WebSocket."""

    async def send(self, event_name: str, payload: dict) -> None:
        await manager.broadcast(
            {"type": "notification", "event": event_name, "data": payload},
            environment_id=payload.get("environment_id"),
        )
