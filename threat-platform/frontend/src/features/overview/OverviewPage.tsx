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
import { useApi } from "@/lib/api/useApi";
import { endpoints } from "@/lib/api/endpoints";
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

  // Section 13: the dashboard refreshes itself rather than waiting to be asked.
  useIntervalRefresh(() => {
    void reload();
    void alerts.reload();
  }, REFRESH_MS);

  if (loading && !data) return <Loading label="Loading dashboard" />;
  if (error) return <ErrorNote message={error} onRetry={reload} />;
  if (!data) return null;

  const { kpis, threats_over_time, severity_distribution, top_sources, environment_status } = data;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <Kpi label="Events processed" value={formatNumber(kpis.total_events)} />
        <Kpi
          label="Threats detected"
          value={formatNumber(kpis.threats_detected)}
          trend={kpis.threats_trend_pct}
        />
        <Kpi label="High risk" value={formatNumber(kpis.high_risk)} tone={SEVERITY_HEX.high} />
        <Kpi label="Under review" value={formatNumber(kpis.under_review)} />
        <Kpi label="Contained" value={formatNumber(kpis.blocked_contained)} tone="#2DD4A7" />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Threats over time · last 24 hours" className="lg:col-span-2">
          <div className="h-56">
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
                  label: key,
                  data: threats_over_time.map((point) => point[key]),
                  borderColor: colour,
                  backgroundColor: `${colour}22`,
                  fill: true,
                  tension: 0.35,
                  pointRadius: 0,
                  borderWidth: 1.5,
                })),
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                  legend: {
                    labels: { color: "#7C8DA0", boxWidth: 8, font: { size: 10 } },
                    position: "bottom",
                  },
                },
                scales: {
                  x: { grid: { color: "#1F2C3A" }, ticks: { color: "#4A5B6E", font: { size: 10 } } },
                  y: {
                    grid: { color: "#1F2C3A" },
                    ticks: { color: "#4A5B6E", font: { size: 10 }, precision: 0 },
                    beginAtZero: true,
                  },
                },
              }}
            />
          </div>
        </Panel>

        <Panel title="By severity">
          {severity_distribution.length === 0 ? (
            <EmptyState title="No threats detected yet" hint="Ingest logs to populate this view." />
          ) : (
            <>
              <div className="mx-auto h-40 w-40">
                <Doughnut
                  data={{
                    labels: severity_distribution.map((slice) => slice.label),
                    datasets: [
                      {
                        data: severity_distribution.map((slice) => slice.count),
                        backgroundColor: severity_distribution.map(
                          (slice) => SEVERITY_HEX[slice.label as Severity] ?? "#7C8DA0",
                        ),
                        borderWidth: 0,
                      },
                    ],
                  }}
                  options={{
                    cutout: "68%",
                    plugins: { legend: { display: false } },
                    maintainAspectRatio: false,
                  }}
                />
              </div>
              <ul className="mt-4 space-y-1.5">
                {severity_distribution.map((slice) => (
                  <li key={slice.label} className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-2">
                      <span
                        className="h-2 w-2 rounded-sm"
                        style={{ background: SEVERITY_HEX[slice.label as Severity] ?? "#7C8DA0" }}
                      />
                      <span className="text-muted">{slice.label}</span>
                    </span>
                    <span className="data">{slice.percent}%</span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </Panel>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="Recent alerts" className="lg:col-span-2">
          {alerts.data && alerts.data.length > 0 ? (
            <Table headers={["Severity", "Detection", "Entity", "Risk", "Seen"]}>
              {alerts.data.map((alert) => (
                <tr key={alert.id} className="align-middle">
                  <td className="py-2 pr-4">
                    <SeverityBadge severity={alert.severity} />
                  </td>
                  <td className="py-2 pr-4">
                    {alert.incident_id ? (
                      <Link
                        to={`/incidents/${alert.incident_id}`}
                        className="text-ink hover:text-accent"
                      >
                        {truncate(alert.title, 46)}
                      </Link>
                    ) : (
                      <span>{truncate(alert.title, 46)}</span>
                    )}
                    <span className="data ml-2 text-faint">{alert.rule_id}</span>
                  </td>
                  <td className="data py-2 pr-4 text-muted">{truncate(alert.entity, 28)}</td>
                  <td className="py-2 pr-4">
                    <RiskScore score={alert.risk_score} factors={alert.risk_factors} />
                  </td>
                  <td className="py-2 text-xs text-muted">{relativeTime(alert.created_at)}</td>
                </tr>
              ))}
            </Table>
          ) : (
            <EmptyState
              title="Nothing detected yet"
              hint="Run scripts/replay_logs.py to push sample logs through the pipeline."
            />
          )}
        </Panel>

        <div className="space-y-4">
          <Panel title="Environment status">
            <ul className="space-y-2.5">
              {environment_status.map((env) => (
                <li key={env.id} className="flex items-center justify-between text-sm">
                  <div className="min-w-0">
                    <p className="truncate text-ink">{env.name}</p>
                    <p className="eyebrow">{env.type}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-xs font-medium ${environmentStatusClasses(env.status)}`}>
                      {env.status}
                    </p>
                    <p className="data text-faint">{env.alerts_last_hour} in 1h</p>
                  </div>
                </li>
              ))}
            </ul>
          </Panel>

          <Panel title="Top sources">
            {top_sources.length === 0 ? (
              <EmptyState title="No repeat offenders" />
            ) : (
              <ul className="space-y-2">
                {top_sources.map((source) => (
                  <li key={source.entity} className="flex items-center justify-between text-xs">
                    <span className="data truncate text-muted">{truncate(source.entity, 24)}</span>
                    <SeverityBadge severity={source.severity} />
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
  trend,
  tone,
}: {
  label: string;
  value: string;
  trend?: number;
  tone?: string;
}) {
  return (
    <div className="panel p-4">
      <p className="eyebrow">{label}</p>
      <p className="mt-1.5 text-2xl font-semibold tabular-nums" style={tone ? { color: tone } : undefined}>
        {value}
      </p>
      {trend !== undefined && (
        <p className={`mt-0.5 text-xs ${trend >= 0 ? "text-sev-high" : "text-ok"}`}>
          {trend >= 0 ? "▲" : "▼"} {Math.abs(trend)}% vs previous day
        </p>
      )}
    </div>
  );
}

import { useEffect, useRef } from "react";

function useIntervalRefresh(callback: () => void, ms: number) {
  const saved = useRef(callback);
  saved.current = callback;
  useEffect(() => {
    const id = window.setInterval(() => saved.current(), ms);
    return () => window.clearInterval(id);
  }, [ms]);
}
