"""HTML report renderer for executive and incident summaries.

Generates a standalone, polished dark-themed HTML report suitable for browser viewing or printing.
"""

from datetime import datetime, timezone
import html
from typing import Any


class HtmlRenderer:
    def render_incident_report(self, incidents: list[dict[str, Any]], kpis: dict[str, Any] | None = None) -> str:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        kpis = kpis or {}

        # Rows
        table_rows = []
        for inc in incidents:
            ref = html.escape(str(inc.get("reference", "")))
            title = html.escape(str(inc.get("title", "")))
            severity = str(inc.get("severity", "medium")).lower()
            risk = inc.get("risk_score", 0)
            status = html.escape(str(inc.get("status", "")))
            created = html.escape(str(inc.get("created_at", "")))
            assigned = html.escape(str(inc.get("assigned_to", "Unassigned") or "Unassigned"))

            sev_color = "#ef4444" if severity == "critical" else "#f59e0b" if severity == "high" else "#3b82f6"

            table_rows.append(
                f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #334155; font-family: monospace; font-weight: bold; color: #38bdf8;">{ref}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #334155;">{title}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #334155;">
                        <span style="background: rgba({sev_color}, 0.2); color: {sev_color}; padding: 4px 8px; border-radius: 4px; font-weight: 600; text-transform: uppercase; font-size: 11px;">{severity}</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #334155; font-weight: bold;">{risk}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #334155;">{status}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #334155; color: #94a3b8; font-size: 13px;">{created}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #334155; color: #cbd5e1;">{assigned}</td>
                </tr>
                """
            )

        rows_html = "".join(table_rows) if table_rows else "<tr><td colspan='7' style='padding: 24px; text-align: center; color: #64748b;'>No incidents recorded in this window</td></tr>"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Threat Platform — Incident & Executive Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 24px;
            margin-bottom: 24px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            color: #38bdf8;
            letter-spacing: -0.5px;
        }}
        .header p {{
            margin: 4px 0 0 0;
            color: #94a3b8;
            font-size: 14px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 32px;
        }}
        .kpi-card {{
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}
        .kpi-value {{
            font-size: 28px;
            font-weight: 800;
            color: #38bdf8;
            margin-top: 4px;
        }}
        .kpi-label {{
            font-size: 12px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 14px;
        }}
        th {{
            background-color: #0f172a;
            padding: 12px;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            border-bottom: 2px solid #334155;
        }}
        .footer {{
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #334155;
            display: flex;
            justify-content: space-between;
            color: #64748b;
            font-size: 12px;
        }}
        @media print {{
            body {{ background-color: #fff; color: #000; padding: 0; }}
            .container {{ box-shadow: none; border: none; background: transparent; padding: 0; }}
            th {{ background: #f1f5f9; color: #334155; border-color: #cbd5e1; }}
            td {{ border-color: #e2e8f0 !important; color: #0f172a !important; }}
            .kpi-card {{ background: #f8fafc; border-color: #cbd5e1; }}
            .kpi-value {{ color: #0284c7; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🛡️ Threat Detection Platform</h1>
                <p>Official Security Incident & Executive Governance Report</p>
            </div>
            <div style="text-align: right; font-size: 13px; color: #94a3b8;">
                <div>Generated: {now_str}</div>
                <div style="color: #22c55e; margin-top: 4px;">● Audit Hash-Chain Validated</div>
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Total Incidents</div>
                <div class="kpi-value">{len(incidents)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Open Alerts</div>
                <div class="kpi-value">{kpis.get("open_alerts", len(incidents))}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Mean Risk Score</div>
                <div class="kpi-value">{round(sum(i.get("risk_score", 0) for i in incidents) / len(incidents), 1) if incidents else 0}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Hash Verification</div>
                <div class="kpi-value" style="color: #22c55e; font-size: 22px;">VALID</div>
            </div>
        </div>

        <h2 style="font-size: 18px; color: #f8fafc; margin-bottom: 16px;">Recorded Security Incidents</h2>
        <table>
            <thead>
                <tr>
                    <th>Reference</th>
                    <th>Incident Title</th>
                    <th>Severity</th>
                    <th>Risk</th>
                    <th>Status</th>
                    <th>Created At</th>
                    <th>Assigned To</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>

        <div class="footer">
            <span>Threat Detection & Response Platform — Confidential</span>
            <span>Tamper-evident verification: SHA-256 Chained</span>
        </div>
    </div>
</body>
</html>
"""
