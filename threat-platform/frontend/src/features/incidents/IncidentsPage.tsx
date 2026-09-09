import { useState } from "react";
import { Link } from "react-router-dom";

import { EmptyState, ErrorNote, Loading, Panel, RiskScore, SeverityBadge, StatusChip, Table } from "@/components/ui";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";
import { relativeTime, truncate } from "@/lib/utils/format";

const FILTERS = ["all", "new", "in_review", "investigating", "decided", "closed"] as const;

export function IncidentsPage() {
  const [status, setStatus] = useState<(typeof FILTERS)[number]>("all");
  const { data, error, loading, reload } = useApi(
    () => endpoints.incidents({ status: status === "all" ? undefined : status, limit: 100 }),
    [status],
  );

  return (
    <Panel
      title="Incidents"
      action={
        <div className="flex flex-wrap gap-1">
          {FILTERS.map((filter) => (
            <button
              key={filter}
              onClick={() => setStatus(filter)}
              className={`rounded border px-2 py-0.5 text-[0.6875rem] transition-colors ${
                status === filter
                  ? "border-accent/50 bg-accent/15 text-accent"
                  : "border-line text-muted hover:text-ink"
              }`}
            >
              {filter.replace(/_/g, " ")}
            </button>
          ))}
        </div>
      }
    >
      {loading && !data ? (
        <Loading label="Loading incidents" />
      ) : error ? (
        <ErrorNote message={error} onRetry={reload} />
      ) : !data || data.length === 0 ? (
        <EmptyState
          title="No incidents in this view"
          hint={status === "all" ? "Incidents open automatically when an alert scores above 50." : "Try another filter."}
        />
      ) : (
        <Table headers={["Reference", "Title", "Severity", "Risk", "Status", "Opened"]}>
          {data.map((incident) => (
            <tr key={incident.id}>
              <td className="data py-2.5 pr-4">
                <Link to={`/incidents/${incident.id}`} className="text-accent hover:underline">
                  {incident.reference}
                </Link>
              </td>
              <td className="py-2.5 pr-4">{truncate(incident.title, 52)}</td>
              <td className="py-2.5 pr-4">
                <SeverityBadge severity={incident.severity} />
              </td>
              <td className="py-2.5 pr-4">
                <RiskScore score={incident.risk_score} />
              </td>
              <td className="py-2.5 pr-4">
                <StatusChip status={incident.status} />
              </td>
              <td className="py-2.5 text-xs text-muted">{relativeTime(incident.created_at)}</td>
            </tr>
          ))}
        </Table>
      )}
    </Panel>
  );
}
