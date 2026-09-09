"""Canonical event schema (Elastic Common Schema-aligned subset).

Everything downstream — detection, correlation, risk — reads only this shape.
Adding a new log source means writing a parser, not touching detection logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class NormalizedEvent:
    raw_event_id: str
    environment_id: str
    timestamp: datetime
    source_type: str

    event_action: str | None = None       # login_failed, file_download, process_start
    event_outcome: str | None = None      # success | failure | unknown
    event_category: str | None = None     # authentication, network, process, file

    source_ip: str | None = None
    destination_ip: str | None = None
    destination_port: int | None = None
    protocol: str | None = None

    user_name: str | None = None
    host_name: str | None = None
    process_name: str | None = None
    file_hash: str | None = None
    url: str | None = None
    bytes_out: int | None = None

    message: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
