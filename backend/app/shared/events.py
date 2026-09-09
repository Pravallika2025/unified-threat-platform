"""Internal domain events — how modules stay decoupled.

A module publishes; interested modules subscribe at startup. No direct imports.
"""

import asyncio
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DomainEvent:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)


Handler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: Handler) -> None:
        self._handlers[event_name].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(event.name, [])
        if not handlers:
            return
        results = await asyncio.gather(
            *(h(event) for h in handlers), return_exceptions=True
        )
        for r in results:
            if isinstance(r, Exception):
                logger.exception("Event handler failed for %s", event.name, exc_info=r)


event_bus = EventBus()

# Event names
EVENT_INGESTED = "event.ingested"
ALERT_RAISED = "alert.raised"
INCIDENT_CREATED = "incident.created"
DECISION_MADE = "decision.made"
ACTION_EXECUTED = "action.executed"
