"""Email notification channel for high-priority security alerts and incidents.

Formats and delivers security event notifications via SMTP.
Safely operates in structured audit mode when SMTP credentials are not configured.
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import smtplib

logger = logging.getLogger(__name__)


class EmailChannel:
    def __init__(
        self,
        smtp_host: str | None = None,
        smtp_port: int = 587,
        smtp_user: str | None = None,
        smtp_password: str | None = None,
        from_addr: str = "alerts@threatplatform.dev",
        to_addr: str | None = None,
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", smtp_port))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_addr = from_addr or os.getenv("SMTP_FROM", "alerts@threatplatform.dev")
        self.to_addr = to_addr or os.getenv("ALERT_EMAIL_RECIPIENT", "soc-team@threatplatform.dev")

    async def send(self, event_name: str, payload: dict) -> None:
        severity = payload.get("severity", "medium")
        # Only email on high or critical events to avoid alert fatigue
        if severity not in {"high", "critical"} and event_name != "INCIDENT_CREATED":
            return

        title = payload.get("title") or f"Security Alert: {event_name}"
        risk_score = payload.get("risk_score", "N/A")
        env_id = payload.get("environment_id", "Default")

        subject = f"[{severity.upper()}] Threat Alert: {title} (Risk: {risk_score})"
        body_text = (
            f"Threat Platform Automated Alert Notification\n"
            f"===========================================\n\n"
            f"Event: {event_name}\n"
            f"Title: {title}\n"
            f"Severity: {severity.upper()}\n"
            f"Risk Score: {risk_score}/100\n"
            f"Environment ID: {env_id}\n\n"
            f"Please review this incident in the Threat Platform SOC Dashboard.\n"
        )

        body_html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #1e293b; border-radius: 8px; border: 1px solid #334155; padding: 24px;">
              <h2 style="color: {'#ef4444' if severity == 'critical' else '#f59e0b'}; margin-top: 0;">{subject}</h2>
              <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
                <tr><td style="padding: 8px 0; color: #94a3b8;">Event:</td><td style="font-weight: bold;">{event_name}</td></tr>
                <tr><td style="padding: 8px 0; color: #94a3b8;">Severity:</td><td style="font-weight: bold; color: {'#ef4444' if severity == 'critical' else '#f59e0b'};">{severity.upper()}</td></tr>
                <tr><td style="padding: 8px 0; color: #94a3b8;">Risk Score:</td><td style="font-weight: bold;">{risk_score} / 100</td></tr>
                <tr><td style="padding: 8px 0; color: #94a3b8;">Environment:</td><td>{env_id}</td></tr>
              </table>
              <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #334155; font-size: 12px; color: #64748b;">
                Threat Detection & Response Platform — Automated Security Dispatch
              </div>
            </div>
          </body>
        </html>
        """

        if not self.smtp_host:
            logger.info("EmailChannel (Mock/Audit Mode): Alert '%s' dispatched to %s", subject, self.to_addr)
            return

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_addr
            msg["To"] = self.to_addr
            msg.attach(MIMEText(body_text, "plain"))
            msg.attach(MIMEText(body_html, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=8) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_addr, [self.to_addr], msg.as_string())
            logger.info("EmailChannel: Delivered alert email for %s to %s", event_name, self.to_addr)
        except Exception as exc:
            logger.warning("Email delivery failed: %s", exc)

    def update_credentials(
        self,
        *,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
        smtp_user: str | None = None,
        smtp_password: str | None = None,
        from_addr: str | None = None,
        to_addr: str | None = None,
    ) -> dict:
        """Dynamically update SMTP credentials at runtime."""
        if smtp_host is not None:
            self.smtp_host = smtp_host.strip()
            os.environ["SMTP_HOST"] = self.smtp_host
        if smtp_port is not None:
            self.smtp_port = int(smtp_port)
            os.environ["SMTP_PORT"] = str(self.smtp_port)
        if smtp_user is not None:
            self.smtp_user = smtp_user.strip()
            os.environ["SMTP_USER"] = self.smtp_user
        if smtp_password is not None:
            self.smtp_password = smtp_password.strip()
            os.environ["SMTP_PASSWORD"] = self.smtp_password
        if from_addr is not None:
            self.from_addr = from_addr.strip()
            os.environ["SMTP_FROM"] = self.from_addr
        if to_addr is not None:
            self.to_addr = to_addr.strip()
            os.environ["ALERT_EMAIL_RECIPIENT"] = self.to_addr

        return self.get_config()

    def get_config(self) -> dict:
        """Return safe SMTP configuration summary without disclosing plain password."""
        return {
            "smtp_host": self.smtp_host or "",
            "smtp_port": self.smtp_port,
            "smtp_user": self.smtp_user or "",
            "from_addr": self.from_addr or "alerts@threatplatform.dev",
            "to_addr": self.to_addr or "soc-team@threatplatform.dev",
            "is_configured": bool(self.smtp_host and self.smtp_user and self.smtp_password),
            "is_mock_mode": not bool(self.smtp_host and self.smtp_user and self.smtp_password),
        }

    async def send_test_email(self, target_to: str | None = None) -> dict:
        """Send an immediate test alert to verify SMTP credentials."""
        recipient = target_to or self.to_addr or "soc-admin@college.edu"
        subject = "[TEST] Threat Detection Platform — Real-Time SMTP Channel Active"
        body_text = (
            "Unified Threat Detection & Response Platform\n"
            "============================================\n\n"
            "This is a verified test alert dispatched over SMTP.\n"
            f"Target Recipient: {recipient}\n"
            f"SMTP Relay Host: {self.smtp_host or 'Simulated Mock Mode'}\n"
            "Status: Real-time threat alert notifications are operational.\n"
        )
        body_html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #1e293b; border-radius: 8px; border: 1px solid #10b981; padding: 24px;">
              <h2 style="color: #10b981; margin-top: 0;">✓ Real-Time SMTP Channel Operational</h2>
              <p style="color: #94a3b8;">This test confirms your SMTP credentials are functioning correctly.</p>
              <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
                <tr><td style="padding: 8px 0; color: #94a3b8;">Recipient:</td><td style="font-weight: bold;">{recipient}</td></tr>
                <tr><td style="padding: 8px 0; color: #94a3b8;">SMTP Host:</td><td style="font-weight: bold; color: #38bdf8;">{self.smtp_host or 'Audit Mock Mode'}</td></tr>
                <tr><td style="padding: 8px 0; color: #94a3b8;">Port:</td><td>{self.smtp_port}</td></tr>
                <tr><td style="padding: 8px 0; color: #94a3b8;">From:</td><td>{self.from_addr}</td></tr>
              </table>
              <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #334155; font-size: 12px; color: #64748b;">
                Unified Multi-Environment Cyber Threat Detection & Response Platform
              </div>
            </div>
          </body>
        </html>
        """

        if not self.smtp_host or not self.smtp_password:
            logger.info("EmailChannel: Test email simulated (audit/mock mode) for %s", recipient)
            return {
                "success": True,
                "mode": "mock",
                "message": f"Test alert logged in Audit Mode for {recipient}. Enter real SMTP credentials to dispatch actual email.",
                "recipient": recipient,
            }

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_addr
            msg["To"] = recipient
            msg.attach(MIMEText(body_text, "plain"))
            msg.attach(MIMEText(body_html, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_addr, [recipient], msg.as_string())

            logger.info("EmailChannel: Real test email successfully sent to %s", recipient)
            return {
                "success": True,
                "mode": "live",
                "message": f"Real test security alert email delivered to {recipient} via {self.smtp_host}!",
                "recipient": recipient,
            }
        except Exception as exc:
            logger.exception("EmailChannel test send failed: %s", exc)
            return {
                "success": False,
                "mode": "error",
                "message": f"SMTP Connection Failed: {str(exc)}",
                "recipient": recipient,
            }

