"""Outbound webhook notification channel with HMAC-SHA256 signing and retry logic."""

import hashlib
import hmac
import json
import logging
import os
import time

logger = logging.getLogger(__name__)


class WebhookChannel:
    def __init__(
        self,
        endpoint_url: str | None = None,
        signing_secret: str | None = None,
        max_retries: int = 3,
    ):
        self.endpoint_url = endpoint_url or os.getenv("WEBHOOK_ALERT_URL")
        self.signing_secret = signing_secret or os.getenv("WEBHOOK_SIGNING_SECRET", "threat-platform-webhook-secret")
        self.max_retries = max_retries

    async def send(self, event_name: str, payload: dict) -> None:
        if not self.endpoint_url:
            logger.debug("WebhookChannel: WEBHOOK_ALERT_URL not configured — skipping outbound dispatch")
            return

        body_bytes = json.dumps(
            {
                "event": event_name,
                "timestamp": time.time(),
                "data": payload,
            },
            sort_keys=True,
        ).encode("utf-8")

        # Compute HMAC signature for tamper verification
        signature = hmac.new(
            self.signing_secret.encode("utf-8"),
            body_bytes,
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-ThreatPlatform-Signature": signature,
            "X-ThreatPlatform-Event": event_name,
        }

        try:
            import httpx

            async with httpx.AsyncClient(timeout=5.0) as client:
                for attempt in range(1, self.max_retries + 1):
                    try:
                        resp = await client.post(self.endpoint_url, content=body_bytes, headers=headers)
                        if resp.status_code < 400:
                            logger.info("WebhookChannel: Delivered %s to %s (attempt %d)", event_name, self.endpoint_url, attempt)
                            return
                    except Exception as err:
                        if attempt == self.max_retries:
                            logger.warning("WebhookChannel delivery failed after %d attempts: %s", attempt, err)
        except ImportError:
            logger.warning("httpx not available for WebhookChannel dispatch")
