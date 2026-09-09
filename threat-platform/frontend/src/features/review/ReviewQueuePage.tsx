import { Link } from "react-router-dom";

import { EmptyState, ErrorNote, Loading, Panel, RiskScore, SeverityBadge, StatusChip } from "@/components/ui";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";
import { humanize, relativeTime } from "@/lib/utils/format";

export function ReviewQueuePage() {
  const queue = useApi(() => endpoints.reviewQueue(false), []);
  const pending = useApi(() => endpoints.pendingApprovals().catch(() => []), []);

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Panel title="Review queue · highest risk first" className="lg:col-span-2">
        {queue.loading && !queue.data ? (
          <Loading label="Loading queue" />
        ) : queue.error ? (
          <ErrorNote message={queue.error} onRetry={queue.reload} />
        ) : !queue.data || queue.data.length === 0 ? (
          <EmptyState title="Queue is clear" hint="Nothing is waiting on an analyst right now." />
        ) : (
          <ul className="space-y-2">
            {queue.data.map((incident) => (
              <li key={incident.id}>
                <Link
                  to={`/incidents/${incident.id}`}
                  className="flex items-center justify-between gap-4 rounded-md border border-line bg-raised px-3 py-2.5 transition-colors hover:border-muted"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm text-ink">{incident.title}</p>
                    <p className="eyebrow mt-0.5">
                      {incident.reference} · opened {relativeTime(incident.created_at)}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-3">
                    <SeverityBadge severity={incident.severity} />
                    <RiskScore score={incident.risk_score} />
                    <StatusChip status={incident.status} />
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Panel>

      <Panel title="Awaiting your approval">
        {!pending.data || pending.data.length === 0 ? (
          <EmptyState
            title="Nothing to approve"
            hint="Destructive actions appear here until a second authorised user signs them off."
          />
        ) : (
          <ul className="space-y-2">
            {pending.data.map((decision) => (
              <li key={decision.id} className="rounded-md border border-sev-medium/40 bg-sev-medium/5 p-3">
                <Link to={`/incidents/${decision.incident_id}`} className="text-sm hover:text-accent">
                  {humanize(decision.action)}
                </Link>
                <p className="mt-1 text-xs text-muted">{decision.justification}</p>
              </li>
            ))}
          </ul>
        )}
      </Panel>
    </div>
  );
}
