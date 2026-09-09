import { useState } from "react";
import { Link } from "react-router-dom";

import { Button, EmptyState, ErrorNote, Loading, Panel, RiskScore, SeverityBadge, Table } from "@/components/ui";
import { Can } from "@/lib/rbac/Can";
import { PERMISSIONS } from "@/lib/rbac/permissions";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";
import { relativeTime, truncate } from "@/lib/utils/format";

export function AlertsPage() {
  const alerts = useApi(() => endpoints.alerts({ limit: 100 }), []);
  const environments = useApi(() => endpoints.environments(), []);
  const [running, setRunning] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  async function runDetection() {
    const environmentId = environments.data?.[0]?.id;
    if (!environmentId) return;
    setRunning(true);
    try {
      const found = await endpoints.runDetection(environmentId, 60);
      setNotice(
        found.length === 0
          ? "Detection ran and found nothing new in the last hour."
          : `Detection produced ${found.length} new alert${found.length === 1 ? "" : "s"}.`,
      );
      await alerts.reload();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Detection failed");
    } finally {
      setRunning(false);
    }
  }

  return (
    <Panel
      title="Alerts"
      action={
        <Can do={PERMISSIONS.INCIDENT_INVESTIGATE}>
          <Button size="sm" onClick={runDetection} disabled={running}>
            {running ? "Running…" : "Run detection now"}
          </Button>
        </Can>
      }
    >
      {notice && <p className="mb-3 text-xs text-muted">{notice}</p>}

      {alerts.loading && !alerts.data ? (
        <Loading label="Loading alerts" />
      ) : alerts.error ? (
        <ErrorNote message={alerts.error} onRetry={alerts.reload} />
      ) : !alerts.data || alerts.data.length === 0 ? (
        <EmptyState
          title="No alerts"
          hint="Ingest logs, then run detection to evaluate them against the rule set."
        />
      ) : (
        <Table headers={["Severity", "Rule", "Detection", "Entity", "Risk", "ATT&CK", "Seen"]}>
          {alerts.data.map((alert) => (
            <tr key={alert.id}>
              <td className="py-2.5 pr-4">
                <SeverityBadge severity={alert.severity} />
              </td>
              <td className="data py-2.5 pr-4 text-muted">{alert.rule_id}</td>
              <td className="py-2.5 pr-4">
                {alert.incident_id ? (
                  <Link to={`/incidents/${alert.incident_id}`} className="hover:text-accent">
                    {truncate(alert.title, 44)}
                  </Link>
                ) : (
                  truncate(alert.title, 44)
                )}
              </td>
              <td className="data py-2.5 pr-4 text-muted">{truncate(alert.entity, 26)}</td>
              <td className="py-2.5 pr-4">
                <RiskScore score={alert.risk_score} factors={alert.risk_factors} />
              </td>
              <td className="data py-2.5 pr-4 text-faint">{alert.attack_technique ?? "—"}</td>
              <td className="py-2.5 text-xs text-muted">{relativeTime(alert.created_at)}</td>
            </tr>
          ))}
        </Table>
      )}
    </Panel>
  );
}
