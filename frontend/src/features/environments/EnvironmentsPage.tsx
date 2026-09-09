import { EmptyState, ErrorNote, Loading, Panel } from "@/components/ui";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";
import { environmentStatusClasses } from "@/lib/utils/severity";

export function EnvironmentsPage() {
  const { data, error, loading, reload } = useApi(() => endpoints.environments(), []);

  if (loading && !data) return <Loading label="Loading environments" />;
  if (error) return <ErrorNote message={error} onRetry={reload} />;
  if (!data || data.length === 0)
    return <EmptyState title="No environments yet" hint="An administrator can add one." />;

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {data.map((environment) => (
        <Panel key={environment.id} title={environment.type}>
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h3 className="text-sm font-medium text-ink">{environment.name}</h3>
              {environment.description && (
                <p className="mt-1 text-xs text-muted">{environment.description}</p>
              )}
            </div>
            <span className={`text-xs font-medium ${environmentStatusClasses(environment.status)}`}>
              {environment.status}
            </span>
          </div>

          <div className="mt-4">
            <p className="eyebrow mb-1.5">Authorised sources</p>
            {environment.authorized_sources.length === 0 ? (
              <p className="text-xs text-sev-medium">
                None authorised — ingestion from this environment will be refused.
              </p>
            ) : (
              <div className="flex flex-wrap gap-1">
                {environment.authorized_sources.map((source) => (
                  <span
                    key={source}
                    className="data rounded border border-line px-1.5 py-0.5 text-xs text-muted"
                  >
                    {source}
                  </span>
                ))}
              </div>
            )}
          </div>
        </Panel>
      ))}
    </div>
  );
}
