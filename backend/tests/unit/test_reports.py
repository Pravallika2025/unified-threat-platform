import pytest

from app.modules.reports.infrastructure.renderers.html_renderer import HtmlRenderer
from app.modules.reports.infrastructure.renderers.pdf_renderer import PdfRenderer


def test_html_and_pdf_renderers():
    incidents = [
        {
            "reference": "INC-000001",
            "title": "SSH Brute Force",
            "severity": "high",
            "risk_score": 85,
            "status": "investigating",
            "created_at": "2026-08-25T12:00:00Z",
            "assigned_to": "analyst@threatplatform.dev",
        }
    ]
    kpis = {"open_alerts": 3}

    # HTML
    html_output = HtmlRenderer().render_incident_report(incidents, kpis)
    assert "INC-000001" in html_output
    assert "SSH Brute Force" in html_output
    assert "Threat Detection Platform" in html_output

    # PDF
    pdf_bytes = PdfRenderer().render_incident_report(incidents, kpis)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-1.4")
    assert b"INC-000001" in pdf_bytes
