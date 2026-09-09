import { EmptyState, ErrorNote, Loading, Panel, Table } from "@/components/ui";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";
import { formatDateTime, truncate } from "@/lib/utils/format";

export function AuditPage() {
  const entries = useApi(() => endpoints.audit(150), []);
  const chain = useApi(() => endpoints.verifyChain(), []);

  return (
    <div className="space-y-4">
      {chain.data && (
        <div
          className={`rounded-md border px-4 py-3 text-sm ${
            chain.data.valid
              ? "border-ok/40 bg-ok/10 text-ok"
              : "border-sev-critical/40 bg-sev-critical/10 text-sev-critical"
          }`}
        >
          {chain.data.valid ? (
            <>
              Audit chain intact — {chain.data.checked} entries verified. Each entry is hashed
              together with the one before it, so any edit to a past entry would break every hash
              that follows.
            </>
          ) : (
            <>
              Audit chain verification failed at entry {chain.data.broken_at}: {chain.data.reason}.
              Treat the log as untrustworthy from that point and investigate database access.
            </>
          )}
        </div>
      )}

      <Panel title="Audit log">
        {entries.loading && !entries.data ? (
          <Loading label="Loading audit log" />
        ) : entries.error ? (
          <ErrorNote message={entries.error} onRetry={entries.reload} />
        ) : !entries.data || entries.data.length === 0 ? (
          <EmptyState title="Nothing recorded yet" />
        ) : (
          <Table headers={["#", "When", "Actor", "Action", "Hash"]}>
            {entries.data.map((entry) => (
              <tr key={entry.id}>
                <td className="data py-2 pr-4 text-faint">{entry.sequence}</td>
                <td className="py-2 pr-4 text-xs text-muted">{formatDateTime(entry.created_at)}</td>
                <td className="data py-2 pr-4 text-muted">
                  {entry.actor_id ? truncate(entry.actor_id, 12) : "system"}
                </td>
                <td className="py-2 pr-4 text-xs">{entry.action}</td>
                <td className="data py-2 text-faint" title={entry.entry_hash}>
                  {entry.entry_hash.slice(0, 12)}…
                </td>
              </tr>
            ))}
          </Table>
        )}
      </Panel>
    </div>
  );
}
