"""Fans alerts out to the UI (implemented) and to email/webhook (stubbed)."""

import logging

from app.modules.notifications.infrastructure.channels.email_channel import EmailChannel
from app.modules.notifications.infrastructure.channels.inapp_channel import InAppChannel
from app.modules.notifications.infrastructure.channels.webhook_channel import WebhookChannel
from app.shared.events import ALERT_RAISED, INCIDENT_CREATED, DomainEvent, event_bus

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.channels = [
            InAppChannel(),
            EmailChannel(),
            WebhookChannel(),
        ]

    async def handle_event(self, event: DomainEvent) -> None:
        for channel in self.channels:
            try:
                await channel.send(event.name, event.payload)
            except Exception:
                logger.exception("Notification channel %s failed", type(channel).__name__)


    def get_email_channel(self) -> EmailChannel | None:
        for channel in self.channels:
            if isinstance(channel, EmailChannel):
                return channel
        return None


notification_service = NotificationService()


def register_notification_handlers() -> None:
    event_bus.subscribe(ALERT_RAISED, notification_service.handle_event)
    event_bus.subscribe(INCIDENT_CREATED, notification_service.handle_event)

