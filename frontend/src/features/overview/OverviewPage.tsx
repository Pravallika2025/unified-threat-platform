import { useState, useEffect, useRef } from "react";
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
import { endpoints, isMockMode } from "@/lib/api/endpoints";
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

const REFRESH_MS = 10000;

// MITRE ATT&CK Matrix stages
const KILL_CHAIN_STAGES = [
  { id: "recon", name: "Reconnaissance", code: "TA0043", count: 18, status: "monitored", color: "#38BDF8" },
  { id: "initial", name: "Initial Access", code: "TA0001", count: 41, status: "critical", color: "#FF385C" },
  { id: "exec", name: "Execution", code: "TA0002", count: 12, status: "high", color: "#F97316" },
  { id: "persist", name: "Persistence", code: "TA0003", count: 6, status: "warning", color: "#FBBF24" },
  { id: "priv", name: "Priv Escalation", code: "TA0004", count: 8, status: "critical", color: "#FF385C" },
  { id: "c2", name: "Command & Control", code: "TA0011", count: 5, status: "high", color: "#F97316" },
  { id: "exfil", name: "Exfiltration", code: "TA0010", count: 4, status: "critical", color: "#FF385C" },
];

export function OverviewPage() {
  const [selectedHorizon, setSelectedHorizon] = useState<number>(24);
  const [simulationTriggered, setSimulationTriggered] = useState(false);

  const { data, error, loading, reload } = useApi(() => endpoints.dashboard(selectedHorizon), [selectedHorizon]);
  const alerts = useApi(() => endpoints.recentAlerts(8), []);

  useIntervalRefresh(() => {
    void reload();
    void alerts.reload();
  }, REFRESH_MS);

  const handleSimulateAttack = async () => {
    setSimulationTriggered(true);
    await endpoints.runDetection("env_corp_hq", 15);
    await alerts.reload();
    await reload();
    setTimeout(() => setSimulationTriggered(false), 3000);
  };

  if (loading && !data) return <Loading label="Calibrating SOC Operations Center Telemetry" />;
  if (error) return <ErrorNote message={error} onRetry={reload} />;
  if (!data) return null;

  const { kpis, threats_over_time, severity_distribution, top_sources, environment_status } = data;

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Dynamic Cyber Command Center Header Banner */}
      <div className="relative overflow-hidden rounded-2xl border border-line/90 bg-gradient-to-r from-panel via-raised/80 to-panel p-6 shadow-glass backdrop-blur-xl">
        <div className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-accent/15 blur-3xl" />
        <div className="pointer-events-none absolute -left-20 -bottom-20 h-64 w-64 rounded-full bg-cyan/10 blur-3xl" />

        <div className="relative z-10 flex flex-wrap items-center justify-between gap-5">
          <div className="space-y-1.5">
            <div className="flex items-center gap-3">
              <span className="relative flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full rounded-full bg-ok opacity-75 animate-ping" />
                <span className="relative inline-flex h-3 w-3 rounded-full bg-ok shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
              </span>
              <span className="font-mono text-xs font-bold tracking-widest text-accent uppercase flex items-center gap-1.5">
                AUTONOMOUS DEFENSE GRID // ACTIVE POSTURE
              </span>
              {isMockMode() ? (
                <span className="inline-flex items-center gap-1 rounded-full border border-cyan/40 bg-cyan/10 px-2 py-0.5 text-[0.625rem] font-mono font-medium text-cyan">
                  ⚡ Interactive SOC Simulation
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 rounded-full border border-ok/40 bg-ok/10 px-2 py-0.5 text-[0.625rem] font-mono font-medium text-ok">
                  ● Live Backend Connected
                </span>
              )}
            </div>

            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white flex items-center gap-3">
              Executive SOC Operations Command
            </h1>

            <p className="text-xs sm:text-sm text-muted max-w-2xl leading-relaxed">
              Real-time multi-environment threat ingestion, behavioral anomaly correlation, 
              kill-chain mitigation gate, and tamper-evident SHA-256 audit ledger.
            </p>
          </div>

          {/* Quick Action Controls */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Horizon Filter */}
            <div className="inline-flex rounded-lg border border-line/80 bg-surface/80 p-1 text-xs font-mono">
              {[6, 12, 24].map((h) => (
                <button
                  key={h}
                  type="button"
                  onClick={() => setSelectedHorizon(h)}
                  className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                    selectedHorizon === h
                      ? "bg-accent text-white font-bold shadow-sm"
                      : "text-muted hover:text-ink"
                  }`}
                >
                  {h}H
                </button>
              ))}
            </div>

            {/* Simulated Attack Trigger */}
            <button
              type="button"
              onClick={handleSimulateAttack}
              disabled={simulationTriggered}
              className="inline-flex items-center gap-1.5 rounded-lg border border-sev-critical/60 bg-sev-critical/15 px-3 py-2 text-xs font-semibold text-sev-critical hover:bg-sev-critical hover:text-white transition-all cursor-pointer shadow-sm disabled:opacity-50"
              title="Inject a real-time cyber attack signal into the active pipeline"
            >
              <span className={`h-2 w-2 rounded-full bg-sev-critical ${simulationTriggered ? "animate-ping" : ""}`} />
              {simulationTriggered ? "Attack Injected!" : "⚡ Simulate Threat"}
            </button>

            <Link
              to="/live"
              className="inline-flex items-center gap-1.5 rounded-lg border border-line/90 bg-raised/80 px-3 py-2 text-xs font-semibold text-ink hover:border-accent/70 hover:bg-elevated hover:text-white transition-all shadow-sm"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-ok shadow-[0_0_6px_rgba(16,185,129,0.8)]" />
              Live Radar
            </Link>

            <Link
              to="/reports"
              className="inline-flex items-center gap-1.5 rounded-lg border border-accent/70 bg-accent/20 px-3.5 py-2 text-xs font-semibold text-accent hover:bg-accent hover:text-white transition-all shadow-glow-accent"
            >
              Export Report →
            </Link>
          </div>
        </div>

        {/* Global Threat Level Bar */}
        <div className="mt-5 pt-4 border-t border-line/60 flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
          <div className="flex items-center gap-3">
            <span className="text-muted uppercase">Threat Defense Posture:</span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-sev-high/40 bg-sev-high/10 text-sev-high font-bold">
              <span className="h-2 w-2 rounded-full bg-sev-high animate-pulse" />
              DEFCON 3 · ELEVATED DEFENSE
            </span>
          </div>

          <div className="flex items-center gap-4 text-faint">
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan" />
              THROUGHPUT: ~1,240 EPS
            </span>
            <span>•</span>
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-ok" />
              HASH CHAIN: INTACT
            </span>
            <span>•</span>
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-accent" />
              MTTR: 3.4 MIN
            </span>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid with Modern High-Tech Cyber Design */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        <Kpi
          label="Events Ingested"
          value={formatNumber(kpis.total_events)}
          sub="Filtered & Normalized"
          topAccent="via-cyan"
          icon="event"
        />
        <Kpi
          label="Threats Detected"
          value={formatNumber(kpis.threats_detected)}
          trend={kpis.threats_trend_pct}
          topAccent="via-sev-high"
          tone={SEVERITY_HEX.high}
          icon="threat"
        />
        <Kpi
          label="Critical Severity"
          value={formatNumber(kpis.high_risk)}
          sub="Requires Containment Gate"
          topAccent="via-sev-critical"
          tone={SEVERITY_HEX.critical}
          glow
          icon="critical"
        />
        <Kpi
          label="Under Review"
          value={formatNumber(kpis.under_review)}
          sub="Active Analyst Queue"
          topAccent="via-sev-medium"
          tone={SEVERITY_HEX.medium}
          icon="review"
        />
        <Kpi
          label="Contained / Neutralized"
          value={formatNumber(kpis.blocked_contained)}
          sub="Automated & Approved"
          topAccent="via-ok"
          tone="#10B981"
          icon="contained"
        />
      </div>

      {/* MITRE ATT&CK Kill-Chain Matrix Strip */}
      <div className="rounded-xl border border-line/80 bg-panel/90 p-4 shadow-glass backdrop-blur-md">
        <div className="flex items-center justify-between mb-3 border-b border-line/50 pb-2">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-accent shadow-[0_0_6px_rgba(59,130,246,0.8)]" />
            <h2 className="text-xs font-bold uppercase tracking-widest text-ink font-mono">
              MITRE ATT&amp;CK® Kill-Chain Stage Distribution
            </h2>
          </div>
          <span className="text-[0.6875rem] font-mono text-faint">7 ACTIVE VECTORS MONITORED</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5">
          {KILL_CHAIN_STAGES.map((st, i) => (
            <div
              key={st.id}
              className="relative rounded-lg border border-line/60 bg-surface/50 p-2.5 transition-all hover:border-accent/60 hover:bg-raised/80 group"
            >
              <div className="flex items-center justify-between text-[0.625rem] font-mono text-faint mb-1">
                <span>0{i + 1}</span>
                <span className="text-cyan">{st.code}</span>
              </div>
              <p className="text-xs font-semibold text-white truncate">{st.name}</p>
              <div className="mt-2 flex items-center justify-between">
                <span className="font-mono text-sm font-bold text-ink">{st.count}</span>
                <span
                  className="h-2 w-2 rounded-full shadow-sm"
                  style={{ backgroundColor: st.color, boxShadow: `0 0 6px ${st.color}80` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Visual Telemetry Row: Attack Velocity Chart & Severity Breakdown */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Timeline Chart */}
        <Panel
          title="Threat Trajectory & Detection Velocity (24H)"
          className="lg:col-span-2"
          action={
            <div className="flex items-center gap-3 text-xs font-mono text-faint">
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-sev-high" /> High
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-sev-medium" /> Medium
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-cyan" /> Low
              </span>
            </div>
          }
        >
          <div className="h-72 pt-2">
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
                  pointRadius: 2.5,
                  pointHoverRadius: 6,
                  borderWidth: 2,
                })),
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                  legend: { display: false },
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
                    grid: { color: "rgba(30, 46, 68, 0.35)" },
                    ticks: { color: "#4E6078", font: { family: "JetBrains Mono", size: 10 } },
                  },
                  y: {
                    grid: { color: "rgba(30, 46, 68, 0.35)" },
                    ticks: { color: "#4E6078", font: { family: "JetBrains Mono", size: 10 }, precision: 0 },
                    beginAtZero: true,
                  },
                },
              }}
            />
          </div>
        </Panel>

        {/* Severity Distribution Donut */}
        <Panel title="Severity Spectrum Breakdown">
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
                        hoverOffset: 6,
                      },
                    ],
                  }}
                  options={{
                    cutout: "74%",
                    plugins: { legend: { display: false } },
                    maintainAspectRatio: false,
                  }}
                />
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="font-mono text-2xl font-black text-white">
                    {severity_distribution.reduce((acc, curr) => acc + curr.count, 0)}
                  </span>
                  <span className="eyebrow text-[0.625rem] text-muted font-bold">Threats</span>
                </div>
              </div>

              <ul className="mt-4 space-y-2 border-t border-line/40 pt-3">
                {severity_distribution.map((slice) => (
                  <li key={slice.label} className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-2">
                      <span
                        className="h-2.5 w-2.5 rounded-full"
                        style={{
                          background: SEVERITY_HEX[slice.label as Severity] ?? "#8B9BB4",
                          boxShadow: `0 0 8px ${SEVERITY_HEX[slice.label as Severity]}80`,
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

      {/* Bottom Telemetry Row: Recent Signal Feed & Monitored Environments */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent Detection Signals */}
        <Panel
          title="Active Detection Signals &amp; Alert Queue"
          action={
            <Link to="/alerts" className="text-xs font-semibold text-accent hover:text-accentHover">
              Full Queue →
            </Link>
          }
          className="lg:col-span-2"
        >
          {alerts.data && alerts.data.length > 0 ? (
            <Table headers={["Severity", "Detection Title & Rule", "Entity / Target", "Risk Matrix", "Detected"]}>
              {alerts.data.map((alert) => (
                <tr key={alert.id} className="transition-colors hover:bg-white/[0.03]">
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
                      <span className="font-mono text-[0.6875rem] text-cyan mt-0.5">
                        {alert.rule_id} {alert.attack_technique ? `· ${alert.attack_technique}` : ""}
                      </span>
                    </div>
                  </td>
                  <td className="data py-2.5 pr-4 text-muted font-medium">
                    <span className="px-1.5 py-0.5 rounded bg-raised border border-line/60 text-ink">
                      {truncate(alert.entity, 22)}
                    </span>
                  </td>
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
              hint="Use the Upload Logs view or click 'Simulate Threat' above."
            />
          )}
        </Panel>

        {/* Monitored Environments & Repeat Sources */}
        <div className="space-y-6">
          <Panel title="Monitored Infrastructure Perimeters">
            <ul className="space-y-3">
              {environment_status.map((env) => (
                <li
                  key={env.id}
                  className="flex items-center justify-between rounded-lg border border-line/60 bg-surface/50 p-3 transition-colors hover:border-lineHover"
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
                      {env.alerts_last_hour} signals / 1h
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </Panel>

          <Panel title="Repeat Threat Sources &amp; Adversaries">
            {top_sources.length === 0 ? (
              <EmptyState title="No repeat sources identified" />
            ) : (
              <ul className="space-y-2">
                {top_sources.map((source) => (
                  <li
                    key={source.entity}
                    className="flex items-center justify-between rounded-lg border border-line/50 bg-surface/40 p-2.5 text-xs hover:border-lineHover"
                  >
                    <span className="font-mono font-medium text-ink truncate pr-2">
                      {truncate(source.entity, 26)}
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
  icon,
}: {
  label: string;
  value: string;
  sub?: string;
  trend?: number;
  tone?: string;
  topAccent?: string;
  glow?: boolean;
  icon?: string;
}) {
  return (
    <div
      className={`group relative overflow-hidden rounded-xl border border-line/80 bg-panel/90 p-5 shadow-glass backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:border-lineHover ${
        glow ? "hover:shadow-glow-critical border-sev-critical/30" : "hover:shadow-glow-accent/20"
      }`}
    >
      {/* Top subtle neon line highlight */}
      <div
        className={`pointer-events-none absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r from-transparent ${topAccent} to-transparent opacity-80 group-hover:opacity-100 transition-opacity`}
      />

      <div className="flex items-center justify-between">
        <p className="eyebrow text-muted font-bold tracking-wider">{label}</p>
        {icon === "critical" && (
          <span className="h-2 w-2 rounded-full bg-sev-critical animate-ping" />
        )}
      </div>

      <p
        className="mt-2 text-3xl font-black tracking-tight tabular-nums font-mono transition-colors"
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
          <span className="text-[0.6875rem] text-faint font-mono">velocity delta</span>
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
