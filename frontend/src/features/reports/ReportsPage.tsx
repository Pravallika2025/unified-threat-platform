import { useState } from "react";

import { Button, EmptyState, ErrorNote, Loading, Panel } from "@/components/ui";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";
import { Can } from "@/lib/rbac/Can";
import { PERMISSIONS } from "@/lib/rbac/permissions";

export function ReportsPage() {
  const summary = useApi(() => endpoints.executiveSummary(), []);
  const environments = useApi(() => endpoints.environments(), []);

  const [selectedEnv, setSelectedEnv] = useState<string>("");
  const [downloading, setDownloading] = useState<string | null>(null);
  const [retentionBusy, setRetentionBusy] = useState(false);
  const [retentionMessage, setRetentionMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async (fmt: "pdf" | "html" | "csv" | "json") => {
    try {
      setDownloading(fmt);
      setError(null);
      await endpoints.downloadReport(fmt, selectedEnv || undefined);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to generate report");
    } finally {
      setDownloading(null);
    }
  };

  const handleEnforceRetention = async () => {
    try {
      setRetentionBusy(true);
      setRetentionMessage(null);
      setError(null);
      const res = await endpoints.enforceRetention();
      setRetentionMessage(
        `Retention enforced: ${res.results.pruned_raw} raw events & ${res.results.pruned_normalized} normalized events pruned. Audit log: ${res.results.audit_log_status}.`,
      );
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to run retention enforcement");
    } finally {
      setRetentionBusy(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-ink">Reports &amp; Compliance</h1>
          <p className="text-sm text-muted">
            Generate executive compliance summaries, export tamper-evident incident reports, and manage data retention.
          </p>
        </div>
      </div>

      {error && <ErrorNote message={error} />}
      {retentionMessage && (
        <div className="rounded-md border border-ok/40 bg-ok/10 px-4 py-3 text-sm text-ok">
          {retentionMessage}
        </div>
      )}

      {/* Executive Summary KPIs */}
      <Panel title="Executive Summary KPIs">
        {summary.loading && !summary.data ? (
          <Loading label="Loading executive summary metrics" />
        ) : summary.error ? (
          <ErrorNote message={summary.error} onRetry={summary.reload} />
        ) : !summary.data ? (
          <EmptyState title="No metrics available" />
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div className="rounded-md border border-line bg-raised p-4">
                <p className="eyebrow">Total Events</p>
                <p className="mt-1 text-2xl font-bold text-ink">
                  {summary.data.kpis.total_events?.toLocaleString() ?? 0}
                </p>
              </div>
              <div className="rounded-md border border-line bg-raised p-4">
                <p className="eyebrow">Threats Detected</p>
                <p className="mt-1 text-2xl font-bold text-sev-high">
                  {summary.data.kpis.threats_detected?.toLocaleString() ?? 0}
                </p>
              </div>
              <div className="rounded-md border border-line bg-raised p-4">
                <p className="eyebrow">Open Incidents</p>
                <p className="mt-1 text-2xl font-bold text-sev-critical">
                  {summary.data.kpis.open_incidents?.toLocaleString() ?? 0}
                </p>
              </div>
              <div className="rounded-md border border-line bg-raised p-4">
                <p className="eyebrow">Contained / Blocked</p>
                <p className="mt-1 text-2xl font-bold text-ok">
                  {summary.data.kpis.blocked_contained?.toLocaleString() ?? 0}
                </p>
              </div>
            </div>
            <p className="text-xs text-faint">{summary.data.note}</p>
          </div>
        )}
      </Panel>

      {/* Incident Report Export */}
      <Panel title="Export Incident Report">
        <div className="space-y-4">
          <div className="max-w-xs">
            <label htmlFor="environment-filter" className="eyebrow mb-1.5 block">
              Scope by Environment
            </label>
            <select
              id="environment-filter"
              value={selectedEnv}
              onChange={(e) => setSelectedEnv(e.target.value)}
              className="w-full rounded-md border border-line bg-raised px-3 py-2 text-sm text-ink"
            >
              <option value="">All Environments</option>
              {environments.data?.map((env) => (
                <option key={env.id} value={env.id}>
                  {env.name} ({env.type})
                </option>
              ))}
            </select>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {/* PDF */}
            <div className="flex flex-col justify-between rounded-md border border-line bg-raised p-4">
              <div>
                <p className="text-sm font-semibold text-ink">PDF Document (.pdf)</p>
                <p className="mt-1 text-xs text-muted">
                  Official binary PDF with cryptographically verified audit verification signature for compliance audits.
                </p>
              </div>
              <Button
                variant="primary"
                size="sm"
                className="mt-4"
                disabled={downloading !== null}
                onClick={() => handleDownload("pdf")}
              >
                {downloading === "pdf" ? "Generating…" : "Download PDF"}
              </Button>
            </div>

            {/* HTML */}
            <div className="flex flex-col justify-between rounded-md border border-line bg-raised p-4">
              <div>
                <p className="text-sm font-semibold text-ink">Interactive HTML (.html)</p>
                <p className="mt-1 text-xs text-muted">
                  Dark-themed standalone SOC security report viewable in any browser with interactive filters.
                </p>
              </div>
              <Button
                size="sm"
                className="mt-4"
                disabled={downloading !== null}
                onClick={() => handleDownload("html")}
              >
                {downloading === "html" ? "Generating…" : "Download HTML"}
              </Button>
            </div>

            {/* CSV */}
            <div className="flex flex-col justify-between rounded-md border border-line bg-raised p-4">
              <div>
                <p className="text-sm font-semibold text-ink">Spreadsheet CSV (.csv)</p>
                <p className="mt-1 text-xs text-muted">
                  Tabular incident export suitable for spreadsheet tools, SIEM bulk imports, and business intelligence.
                </p>
              </div>
              <Button
                size="sm"
                className="mt-4"
                disabled={downloading !== null}
                onClick={() => handleDownload("csv")}
              >
                {downloading === "csv" ? "Generating…" : "Download CSV"}
              </Button>
            </div>

            {/* JSON */}
            <div className="flex flex-col justify-between rounded-md border border-line bg-raised p-4">
              <div>
                <p className="text-sm font-semibold text-ink">Structured JSON (.json)</p>
                <p className="mt-1 text-xs text-muted">
                  Full programmatic schema payload containing incident records and evidence hashes for automation.
                </p>
              </div>
              <Button
                size="sm"
                className="mt-4"
                disabled={downloading !== null}
                onClick={() => handleDownload("json")}
              >
                {downloading === "json" ? "Generating…" : "Download JSON"}
              </Button>
            </div>
          </div>
        </div>
      </Panel>

      {/* Data Retention Management */}
      <Can do={PERMISSIONS.SETTINGS_MANAGE}>
        <Panel title="Data Retention &amp; Lifecycle">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="max-w-xl">
              <p className="text-sm font-medium text-ink">Enforce Retention Policy</p>
              <p className="mt-0.5 text-xs text-muted">
                Prunes expired raw events older than 90 days and normalized events older than 180 days.
                Events attached to active incidents are strictly preserved, and the immutable audit log chain is protected.
              </p>
            </div>
            <Button
              variant="danger"
              size="sm"
              disabled={retentionBusy}
              onClick={handleEnforceRetention}
            >
              {retentionBusy ? "Pruning…" : "Enforce retention now"}
            </Button>
          </div>
        </Panel>
      </Can>
    </div>
  );
}
