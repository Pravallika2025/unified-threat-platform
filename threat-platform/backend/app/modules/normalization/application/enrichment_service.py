"""Adds context the raw log did not carry: geo, asset criticality, identity.

TODO: wire a real GeoIP database (MaxMind) and an asset inventory source.
Kept deliberately thin so detection stays deterministic in tests.
"""

from app.shared.utils.ip import is_private


class EnrichmentService:
    def enrich(self, event_fields: dict) -> dict:
        source_ip = event_fields.get("source_ip")
        if source_ip:
            event_fields.setdefault("source_is_internal", is_private(source_ip))
        return event_fields
