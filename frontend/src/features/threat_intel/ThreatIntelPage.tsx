import { useState } from "react";

import {
  Button,
  EmptyState,
  ErrorNote,
  Loading,
  Panel,
  SeverityBadge,
  Table,
} from "@/components/ui";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";
import { Can } from "@/lib/rbac/Can";
import { PERMISSIONS } from "@/lib/rbac/permissions";
import { formatDateTime, truncate } from "@/lib/utils/format";
import type { Severity } from "@/types/api";

export function ThreatIntelPage() {
  const indicators = useApi(() => endpoints.threatIntel(), []);

  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [syncing, setSyncing] = useState(false);
  const [syncNotice, setSyncNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // New indicator form state
  const [showForm, setShowForm] = useState(false);
  const [val, setVal] = useState("");
  const [iocType, setIocType] = useState("ip");
  const [source, setSource] = useState("analyst_manual");
  const [confidence, setConfidence] = useState(85);
  const [sev, setSev] = useState<Severity>("high");
  const [desc, setDesc] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSync = async () => {
    try {
      setSyncing(true);
      setError(null);
      setSyncNotice(null);
      const res = await endpoints.syncFeeds();
      const summary = Object.entries(res.results)
        .map(([k, v]) => `${k}: +${v}`)
        .join(", ");
      setSyncNotice(`Feeds synchronized successfully. Added: ${summary || "0 new"}.`);
      await indicators.reload();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to sync feeds");
    } finally {
      setSyncing(false);
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!val.trim()) return;

    try {
      setSaving(true);
      setError(null);
      await endpoints.addIndicators([
        {
          value: val.trim().toLowerCase(),
          type: iocType,
          source: source.trim() || "analyst_manual",
          confidence: Number(confidence),
          severity: sev,
          description: desc.trim() || null,
        },
      ]);
      setVal("");
      setDesc("");
      setShowForm(false);
      await indicators.reload();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to add indicator");
    } finally {
      setSaving(false);
    }
  };

  const filtered = (indicators.data ?? []).filter((ioc) => {
    const matchesSearch =
      ioc.value.toLowerCase().includes(search.toLowerCase()) ||
      (ioc.description ?? "").toLowerCase().includes(search.toLowerCase()) ||
      ioc.source.toLowerCase().includes(search.toLowerCase());
    const matchesType = typeFilter === "all" || ioc.type.toLowerCase() === typeFilter.toLowerCase();
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-ink">Threat Intelligence</h1>
          <p className="text-sm text-muted">
            Global and curated Indicators of Compromise (IOCs), external feed sync, and signature detection index.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Can do={PERMISSIONS.SETTINGS_MANAGE}>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowForm(!showForm)}
            >
              {showForm ? "Cancel" : "Add indicator"}
            </Button>
            <Button
              variant="primary"
              size="sm"
              disabled={syncing}
              onClick={handleSync}
            >
              {syncing ? "Syncing feeds…" : "Sync external feeds"}
            </Button>
          </Can>
        </div>
      </div>

      {error && <ErrorNote message={error} />}
      {syncNotice && (
        <div className="rounded-md border border-ok/40 bg-ok/10 px-4 py-3 text-sm text-ok">
          {syncNotice}
        </div>
      )}

      {/* Manual Indicator Addition Form */}
      {showForm && (
        <Panel title="Add Custom Threat Indicator">
          <form onSubmit={handleAdd} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="sm:col-span-2">
                <label htmlFor="ioc-value" className="eyebrow mb-1.5 block">
                  Indicator Value (IP, domain, hash, email, URL)
                </label>
                <input
                  id="ioc-value"
                  type="text"
                  required
                  placeholder="e.g. 198.51.100.23 or malicious-domain.com"
                  value={val}
                  onChange={(e) => setVal(e.target.value)}
                  className="w-full rounded-md border border-line bg-raised px-3 py-2 text-sm text-ink placeholder:text-faint"
                />
              </div>

              <div>
                <label htmlFor="ioc-type" className="eyebrow mb-1.5 block">
                  Type
                </label>
                <select
                  id="ioc-type"
                  value={iocType}
                  onChange={(e) => setIocType(e.target.value)}
                  className="w-full rounded-md border border-line bg-raised px-3 py-2 text-sm text-ink"
                >
                  <option value="ip">IP Address</option>
                  <option value="domain">Domain</option>
                  <option value="hash">SHA-256 Hash</option>
                  <option value="email">Email</option>
                  <option value="url">URL</option>
                </select>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <label htmlFor="ioc-source" className="eyebrow mb-1.5 block">
                  Source Name
                </label>
                <input
                  id="ioc-source"
                  type="text"
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  className="w-full rounded-md border border-line bg-raised px-3 py-2 text-sm text-ink"
                />
              </div>

              <div>
                <label htmlFor="ioc-confidence" className="eyebrow mb-1.5 block">
                  Confidence (0 - 100)
                </label>
                <input
                  id="ioc-confidence"
                  type="number"
                  min="0"
                  max="100"
                  value={confidence}
                  onChange={(e) => setConfidence(Number(e.target.value))}
                  className="w-full rounded-md border border-line bg-raised px-3 py-2 text-sm text-ink"
                />
              </div>

              <div>
                <label htmlFor="ioc-severity" className="eyebrow mb-1.5 block">
                  Severity
                </label>
                <select
                  id="ioc-severity"
                  value={sev}
                  onChange={(e) => setSev(e.target.value as Severity)}
                  className="w-full rounded-md border border-line bg-raised px-3 py-2 text-sm text-ink"
                >
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>

            <div>
              <label htmlFor="ioc-description" className="eyebrow mb-1.5 block">
                Description / Context
              </label>
              <input
                id="ioc-description"
                type="text"
                placeholder="Observed in phishing campaign / C2 node"
                value={desc}
                onChange={(e) => setDesc(e.target.value)}
                className="w-full rounded-md border border-line bg-raised px-3 py-2 text-sm text-ink placeholder:text-faint"
              />
            </div>

            <div className="flex justify-end gap-2">
              <Button size="sm" type="button" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
              <Button size="sm" variant="primary" type="submit" disabled={saving}>
                {saving ? "Saving…" : "Save indicator"}
              </Button>
            </div>
          </form>
        </Panel>
      )}

      {/* Filters & Search */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-1 items-center gap-3">
          <input
            type="search"
            placeholder="Search indicator value, source, or description…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full max-w-sm rounded-md border border-line bg-panel px-3 py-2 text-sm text-ink placeholder:text-faint"
          />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="rounded-md border border-line bg-panel px-3 py-2 text-sm text-ink"
          >
            <option value="all">All Types</option>
            <option value="ip">IP</option>
            <option value="domain">Domain</option>
            <option value="hash">Hash</option>
            <option value="email">Email</option>
            <option value="url">URL</option>
          </select>
        </div>

        <p className="eyebrow text-faint">
          Showing {filtered.length} of {indicators.data?.length ?? 0} indicators
        </p>
      </div>

      {/* Indicators Table */}
      <Panel title="Active Indicators Index">
        {indicators.loading && !indicators.data ? (
          <Loading label="Loading threat intelligence index" />
        ) : indicators.error ? (
          <ErrorNote message={indicators.error} onRetry={indicators.reload} />
        ) : filtered.length === 0 ? (
          <EmptyState title="No indicators match your filter" />
        ) : (
          <Table headers={["Severity", "Type", "Indicator", "Source", "Confidence", "Description", "First seen"]}>
            {filtered.map((ioc) => (
              <tr key={ioc.id} className="border-b border-line/40">
                <td className="py-2.5 pr-4">
                  <SeverityBadge severity={ioc.severity} />
                </td>
                <td className="py-2.5 pr-4 font-mono text-xs uppercase text-muted">{ioc.type}</td>
                <td className="py-2.5 pr-4 font-mono text-xs font-semibold text-ink">
                  {truncate(ioc.value, 40)}
                </td>
                <td className="py-2.5 pr-4 text-xs text-muted">{ioc.source}</td>
                <td className="py-2.5 pr-4 text-xs">
                  <span className="data font-medium text-ink">{ioc.confidence}%</span>
                </td>
                <td className="py-2.5 pr-4 text-xs text-muted" title={ioc.description ?? ""}>
                  {truncate(ioc.description ?? "—", 45)}
                </td>
                <td className="py-2.5 text-xs text-faint">
                  {formatDateTime(ioc.first_seen)}
                </td>
              </tr>
            ))}
          </Table>
        )}
      </Panel>
    </div>
  );
}
