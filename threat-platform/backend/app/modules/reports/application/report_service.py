"""Report generation — section 12.

JSON and CSV are implemented. PDF/HTML rendering is stubbed; see renderers/.
"""

import csv
import io
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.modules.dashboard.application.metrics_service import MetricsService
from app.modules.incidents.application.incident_service import IncidentService

SUPPORTED_FORMATS = {"json", "csv"}


class ReportService:
    def __init__(self, db: AsyncSession):
        self.incidents = IncidentService(db)
        self.metrics = MetricsService(db)

    async def incident_report(self, *, fmt: str = "json", environment_id: str | None = None):
        if fmt not in SUPPORTED_FORMATS:
            raise ValidationError(
                f"Unsupported format '{fmt}'. Available now: {sorted(SUPPORTED_FORMATS)}. "
                "PDF rendering is not implemented yet."
            )

        incidents = await self.incidents.list(environment_id=environment_id, limit=1000)
        rows = [
            {
                "reference": i.reference,
                "title": i.title,
                "severity": i.severity,
                "risk_score": i.risk_score,
                "status": i.status,
                "environment_id": i.environment_id,
                "assigned_to": i.assigned_to or "",
                "created_at": i.created_at.isoformat(),
                "closed_at": i.closed_at.isoformat() if i.closed_at else "",
            }
            for i in incidents
        ]

        if fmt == "json":
            return json.dumps({"incidents": rows, "count": len(rows)}, indent=2), "application/json"

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()) if rows else ["reference"])
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue(), "text/csv"

    async def executive_summary(self) -> dict:
        kpis = await self.metrics.kpis()
        return {
            "generated_for": "executive",
            "kpis": kpis,
            "note": "Figures are computed live from the incident and alert tables.",
        }
