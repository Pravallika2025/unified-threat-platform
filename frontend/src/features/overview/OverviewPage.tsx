import { useEffect, useRef } from "react";
import {
  ArcElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from "chart.js";
import { Doughnut, Line } from "react-chartjs-2";
import { Link } from "react-router-dom";

import {
  EmptyState,
  ErrorNote,
  Loading,
  Panel,
  RiskScore,
  SeverityBadge,
  Table,
} from "@/components/ui";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";
import { formatNumber, relativeTime, truncate } from "@/lib/utils/format";
import { SEVERITY_HEX, environmentStatusClasses } from "@/lib/utils/severity";
import type { Severity } from "@/types/api";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Filler,
  Tooltip,
  Legend,
);

const REFRESH_MS = 15000;

export function OverviewPage() {
  const { data, error, loading, reload } = useApi(() => endpoints.dashboard(24), []);
  const alerts = useApi(() => endpoints.recentAlerts(8), []);

  useIntervalRefresh(() => {
    void reload();
    void alerts.reload();
  }, REFRESH_MS);

  if (loading && !data) return <Loading label="Initializing Threat Telemetry" />;
  if (error) return <ErrorNote message={error} onRetry={reload} />;
  if (!data) return null;

  const { kpis, threats_over_time, severity_distribution, top_sources, environment_status } = data;

  return (
    <div className="space-y-6">
      {/* Hero Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-line/60 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full rounded-full bg-accent opacity-75 animate-ping" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-accent" />
            </span>
            <span className="font-mono text-xs font-semibold tracking-widest text-accent uppercase">
              Unified Threat Telemetry Grid
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
            SOC Operations Center
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/live"
            className="inline-flex items-center gap-2 rounded-lg border border-line/80 bg-raised/70 px-3.5 py-2 text-xs font-semibold text-ink shadow-sm transition-all hover:border-accent/60 hover:bg-elevated hover:text-white"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-ok shadow-[0_0_6px_rgba(16,185,129,0.8)]" />
            Open Live Monitor
          </Link>
          <Link
            to="/reports"
            className="inline-flex items-center gap-2 rounded-lg border border-accent/70 bg-accent/20 px-3.5 py-2 text-xs font-semibold text-accent shadow-glow-accent hover:bg-accent hover:text-white transition-all"
          >
            Export Compliance Report →
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        <Kpi
          label="Events Processed"
          value={formatNumber(kpis.total_events)}
          sub="Last 24 hours"
          topAccent="via-cyan"
        />
        <Kpi
          label="Threats Detected"
          value={formatNumber(kpis.threats_detected)}
          trend={kpis.threats_trend_pct}
          topAccent="via-sev-high"
          tone={SEVERITY_HEX.high}
        />
        <Kpi
          label="High Risk Threats"
          value={formatNumber(kpis.high_risk)}
          sub="Requires immediate review"
          topAccent="via-sev-critical"
          tone={SEVERITY_HEX.critical}
          glow
        />
        <Kpi
          label="Under Investigation"
          value={formatNumber(kpis.under_review)}
          sub="Active analyst review"
          topAccent="via-sev-medium"
          tone={SEVERITY_HEX.medium}
        />
        <Kpi
          label="Contained / Blocked"
          value={formatNumber(kpis.blocked_contained)}
          sub="Automated mitigations"
          topAccent="via-ok"
          tone="#10B981"
        />
      </div>

      {/* Main Visual Telemetry Row */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Timeline Chart */}
        <Panel title="Threat Frequency & Velocity · 24-Hour Horizon" className="lg:col-span-2">
          <div className="h-64 pt-2">
            <Line
              data={{
                labels: threats_over_time.map((point) => point.time),
                datasets: (
                  [
                    ["high", SEVERITY_HEX.high],
                    ["medium", SEVERITY_HEX.medium],
                    ["low", SEVERITY_HEX.low],
                  ] as const
                ).map(([key, colour]) => ({
                  label: key.toUpperCase(),
                  data: threats_over_time.map((point) => point[key]),
                  borderColor: colour,
                  backgroundColor: `${colour}18`,
                  fill: true,
                  tension: 0.35,
                  pointRadius: 2,
                  pointHoverRadius: 6,
                  borderWidth: 2,
                })),
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                  legend: {
                    labels: {
                      color: "#8B9BB4",
                      boxWidth: 10,
                      font: { family: "Inter", size: 11 },
                    },
                    position: "bottom",
                  },
                  tooltip: {
                    backgroundColor: "#0F1724",
                    titleColor: "#F0F6FC",
                    bodyColor: "#8B9BB4",
                    borderColor: "#1E2E44",
                    borderWidth: 1,
                    padding: 10,
                  },
                },
                scales: {
                  x: {
                    grid: { color: "rgba(30, 46, 68, 0.4)" },
                    ticks: { color: "#4E6078", font: { family: "JetBrains Mono", size: 10 } },
                  },
                  y: {
                    grid: { color: "rgba(30, 46, 68, 0.4)" },
                    ticks: { color: "#4E6078", font: { family: "JetBrains Mono", size: 10 }, precision: 0 },
                    beginAtZero: true,
                  },
                },
              }}
            />
          </div>
        </Panel>

        {/* Severity Doughnut */}
        <Panel title="Severity Distribution">
          {severity_distribution.length === 0 ? (
            <EmptyState title="No active threats" hint="Ingest security logs to populate telemetry." />
          ) : (
            <div className="flex flex-col justify-between h-full pt-1">
              <div className="relative mx-auto h-44 w-44">
                <Doughnut
                  data={{
                    labels: severity_distribution.map((slice) => slice.label),
                    datasets: [
                      {
                        data: severity_distribution.map((slice) => slice.count),
                        backgroundColor: severity_distribution.map(
                          (slice) => SEVERITY_HEX[slice.label as Severity] ?? "#8B9BB4",
                        ),
                        borderColor: "#0F1724",
                        borderWidth: 3,
                        hoverOffset: 4,
                      },
                    ],
                  }}
                  options={{
                    cutout: "72%",
                    plugins: { legend: { display: false } },
                    maintainAspectRatio: false,
                  }}
                />
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="font-mono text-xl font-bold text-white">
                    {severity_distribution.reduce((acc, curr) => acc + curr.count, 0)}
                  </span>
                  <span className="eyebrow text-[0.5625rem] text-muted">Total</span>
                </div>
              </div>

              <ul className="mt-4 space-y-2 border-t border-line/40 pt-3">
                {severity_distribution.map((slice) => (
                  <li key={slice.label} className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-2">
                      <span
                        className="h-2 w-2 rounded-full"
                        style={{
                          background: SEVERITY_HEX[slice.label as Severity] ?? "#8B9BB4",
                          boxShadow: `0 0 8px ${SEVERITY_HEX[slice.label as Severity]}66`,
                        }}
                      />
                      <span className="font-medium text-ink capitalize">{slice.label}</span>
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-muted font-mono">{slice.count}</span>
                      <span className="data font-semibold text-ink bg-raised/70 px-1.5 py-0.5 rounded border border-line/50">
                        {slice.percent}%
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Panel>
      </div>

      {/* Bottom Telemetry Row: Recent Alerts & Environment Matrix */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent Alerts Feed */}
        <Panel
          title="Recent Detection Signals"
          action={
            <Link to="/alerts" className="text-xs font-medium text-accent hover:text-accentHover">
              View all alerts →
            </Link>
          }
          className="lg:col-span-2"
        >
          {alerts.data && alerts.data.length > 0 ? (
            <Table headers={["Severity", "Rule & Title", "Entity", "Risk", "Time"]}>
              {alerts.data.map((alert) => (
                <tr key={alert.id} className="transition-colors hover:bg-white/[0.02]">
                  <td className="py-2.5 px-4">
                    <SeverityBadge severity={alert.severity} />
                  </td>
                  <td className="py-2.5 pr-4">
                    <div className="flex flex-col">
                      {alert.incident_id ? (
                        <Link
                          to={`/incidents/${alert.incident_id}`}
                          className="font-medium text-ink hover:text-accent transition-colors"
                        >
                          {truncate(alert.title, 42)}
                        </Link>
                      ) : (
                        <span className="font-medium text-ink">{truncate(alert.title, 42)}</span>
                      )}
                      <span className="font-mono text-[0.6875rem] text-cyan/90 mt-0.5">{alert.rule_id}</span>
                    </div>
                  </td>
                  <td className="data py-2.5 pr-4 text-muted font-medium">{truncate(alert.entity, 24)}</td>
                  <td className="py-2.5 pr-4">
                    <RiskScore score={alert.risk_score} factors={alert.risk_factors} />
                  </td>
                  <td className="py-2.5 pr-4 text-xs font-mono text-faint">
                    {relativeTime(alert.created_at)}
                  </td>
                </tr>
              ))}
            </Table>
          ) : (
            <EmptyState
              title="No alerts detected in current window"
              hint="Use the Upload Logs view to ingest log feeds or trigger automated detection."
            />
          )}
        </Panel>

        {/* Environment Status & Top Attack Sources */}
        <div className="space-y-6">
          <Panel title="Monitored Environments">
            <ul className="space-y-3">
              {environment_status.map((env) => (
                <li
                  key={env.id}
                  className="flex items-center justify-between rounded-lg border border-line/50 bg-surface/40 p-3 transition-colors hover:border-lineHover"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-white">{env.name}</p>
                    <span className="inline-block mt-0.5 font-mono text-[0.625rem] uppercase tracking-wider text-muted">
                      {env.type}
                    </span>
                  </div>
                  <div className="text-right">
                    <span
                      className={`inline-block rounded-full border px-2 py-0.5 text-[0.625rem] font-semibold uppercase tracking-wider ${environmentStatusClasses(
                        env.status,
                      )}`}
                    >
                      {env.status}
                    </span>
                    <p className="font-mono text-[0.6875rem] text-muted mt-1">
                      {env.alerts_last_hour} alerts / 1h
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </Panel>

          <Panel title="Repeat Attack Vectors &amp; Sources">
            {top_sources.length === 0 ? (
              <EmptyState title="No repeat sources identified" />
            ) : (
              <ul className="space-y-2">
                {top_sources.map((source) => (
                  <li
                    key={source.entity}
                    className="flex items-center justify-between rounded-lg border border-line/40 bg-surface/30 p-2.5 text-xs hover:border-lineHover"
                  >
                    <span className="font-mono font-medium text-ink truncate pr-2">
                      {truncate(source.entity, 22)}
                    </span>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className="font-mono text-muted text-[0.6875rem]">{source.count} hits</span>
                      <SeverityBadge severity={source.severity} />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </Panel>
        </div>
      </div>
    </div>
  );
}

function Kpi({
  label,
  value,
  sub,
  trend,
  tone,
  topAccent = "via-accent",
  glow = false,
}: {
  label: string;
  value: string;
  sub?: string;
  trend?: number;
  tone?: string;
  topAccent?: string;
  glow?: boolean;
}) {
  return (
    <div
      className={`group relative overflow-hidden rounded-xl border border-line/80 bg-panel/85 p-5 shadow-glass backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:border-lineHover ${
        glow ? "hover:shadow-glow-critical" : "hover:shadow-glow-accent/20"
      }`}
    >
      {/* Top subtle neon line highlight */}
      <div
        className={`pointer-events-none absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r from-transparent ${topAccent} to-transparent opacity-80 group-hover:opacity-100 transition-opacity`}
      />

      <p className="eyebrow text-muted font-semibold tracking-wider">{label}</p>
      
      <p
        className="mt-2 text-3xl font-extrabold tracking-tight tabular-nums font-mono transition-colors"
        style={tone ? { color: tone } : { color: "#F0F6FC" }}
      >
        {value}
      </p>

      {trend !== undefined ? (
        <div className="mt-2 flex items-center gap-1.5">
          <span
            className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[0.6875rem] font-bold ${
              trend >= 0
                ? "bg-sev-high/15 text-sev-high border border-sev-high/30"
                : "bg-ok/15 text-ok border border-ok/30"
            }`}
          >
            {trend >= 0 ? "▲" : "▼"} {Math.abs(trend)}%
          </span>
          <span className="text-[0.6875rem] text-faint">vs 24h prior</span>
        </div>
      ) : sub ? (
        <p className="mt-2 text-[0.6875rem] text-faint font-medium">{sub}</p>
      ) : null}
    </div>
  );
}

function useIntervalRefresh(callback: () => void, ms: number) {
  const saved = useRef(callback);
  saved.current = callback;
  useEffect(() => {
    const id = window.setInterval(() => saved.current(), ms);
    return () => window.clearInterval(id);
  }, [ms]);
}
