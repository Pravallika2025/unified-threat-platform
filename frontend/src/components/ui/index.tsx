import type { ButtonHTMLAttributes, ReactNode } from "react";

import { severityClasses, SEVERITY_HEX } from "@/lib/utils/severity";

export function Panel({
  title,
  action,
  children,
  className = "",
}: {
  title?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`relative overflow-hidden rounded-xl border border-line/80 bg-panel/85 backdrop-blur-md shadow-glass transition-all duration-200 hover:border-lineHover/80 ${className}`}>
      {/* Subtle top ambient highlight */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/15 to-transparent" />
      
      {(title || action) && (
        <header className="flex items-center justify-between border-b border-line/60 bg-surface/40 px-5 py-3.5">
          {title && (
            <div className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-accent shadow-[0_0_8px_rgba(59,130,246,0.8)]" />
              <h2 className="eyebrow tracking-wider text-muted font-semibold">{title}</h2>
            </div>
          )}
          {action}
        </header>
      )}
      <div className="p-5">{children}</div>
    </section>
  );
}

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost" | "danger";
  size?: "sm" | "md";
};

export function Button({
  variant = "ghost",
  size = "md",
  className = "",
  ...props
}: ButtonProps) {
  const base =
    "relative inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.98] cursor-pointer";
  const sizes = size === "sm" ? "px-3 py-1.5 text-xs" : "px-4 py-2 text-sm";
  const variants = {
    primary:
      "bg-accent text-white border border-accent/80 shadow-glow-accent hover:bg-accentHover hover:shadow-[0_0_25px_rgba(59,130,246,0.6)] hover:-translate-y-0.5",
    ghost:
      "bg-raised/70 border border-line/90 text-ink hover:border-lineHover hover:bg-elevated hover:text-white hover:-translate-y-0.5 shadow-sm",
    danger:
      "bg-sev-critical/15 border border-sev-critical/50 text-sev-critical hover:bg-sev-critical/25 shadow-glow-critical hover:-translate-y-0.5",
  }[variant];

  return <button className={`${base} ${sizes} ${variants} ${className}`} {...props} />;
}

export function SeverityBadge({ severity }: { severity: string }) {
  const sev = severity.toLowerCase();
  const dotColor =
    sev === "critical"
      ? "bg-sev-critical shadow-[0_0_8px_rgba(255,56,92,0.8)]"
      : sev === "high"
        ? "bg-sev-high shadow-[0_0_8px_rgba(249,115,22,0.8)]"
        : sev === "medium"
          ? "bg-sev-medium shadow-[0_0_8px_rgba(251,191,36,0.8)]"
          : "bg-sev-low shadow-[0_0_8px_rgba(56,189,248,0.8)]";

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[0.6875rem] font-medium uppercase tracking-wider ${severityClasses(severity)}`}
    >
      <span className={`mr-1.5 inline-block h-1.5 w-1.5 rounded-full ${dotColor}`} />
      {severity}
    </span>
  );
}

export function StatusChip({ status }: { status: string }) {
  const isOk = status === "action_executed" || status === "closed";
  const isMuted = status === "dismissed";
  
  const tone = isOk
    ? "text-ok border-ok/40 bg-ok/10"
    : isMuted
      ? "text-muted border-line bg-raised/40"
      : "text-accent border-accent/40 bg-accent/10 shadow-[0_0_10px_rgba(59,130,246,0.15)]";

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[0.6875rem] font-medium tracking-wide ${tone}`}>
      <span className={`mr-1.5 h-1.5 w-1.5 rounded-full ${isOk ? "bg-ok" : isMuted ? "bg-muted" : "bg-accent"}`} />
      {status.replace(/_/g, " ")}
    </span>
  );
}

export function RiskScore({
  score,
  factors,
}: {
  score: number;
  factors?: Record<string, number>;
}) {
  const hex =
    score >= 80 ? SEVERITY_HEX.critical : score >= 60 ? SEVERITY_HEX.high : score >= 35 ? SEVERITY_HEX.medium : SEVERITY_HEX.low;
  const entries = Object.entries(factors ?? {});

  return (
    <div className="group relative inline-flex items-center gap-2.5">
      <div className="h-2 w-20 overflow-hidden rounded-full bg-raised/80 border border-line/60 p-[1px]">
        <div
          className="h-full rounded-full transition-all duration-500 shadow-[0_0_10px_currentColor]"
          style={{ width: `${Math.min(score, 100)}%`, backgroundColor: hex, color: hex }}
        />
      </div>
      <span className="data font-bold text-xs tracking-tight" style={{ color: hex }}>
        {score}
      </span>

      {entries.length > 0 && (
        <div className="pointer-events-none absolute left-0 top-7 z-30 hidden w-64 rounded-xl border border-line/90 bg-panel/95 p-3.5 shadow-2xl backdrop-blur-md group-hover:block animate-in fade-in zoom-in-95">
          <p className="eyebrow mb-2 text-ink font-semibold flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-accent" />
            Risk Factor Breakdown
          </p>
          <dl className="space-y-1.5">
            {entries.map(([key, value]) => (
              <div key={key} className="flex justify-between text-xs border-b border-line/30 pb-1">
                <dt className="text-muted">{key.replace(/_/g, " ")}</dt>
                <dd className="data text-ink font-semibold">{value}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </div>
  );
}

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="py-14 text-center">
      <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full border border-line/80 bg-raised/60 text-muted">
        <svg className="h-5 w-5 opacity-60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
      </div>
      <p className="text-sm font-medium text-ink">{title}</p>
      {hint && <p className="mt-1 text-xs text-muted max-w-sm mx-auto">{hint}</p>}
    </div>
  );
}

export function Loading({ label = "Loading" }: { label?: string }) {
  return (
    <div className="py-12 flex flex-col items-center justify-center gap-3">
      <div className="relative h-7 w-7">
        <div className="absolute inset-0 rounded-full border-2 border-line/60 border-t-accent animate-spin" />
        <div className="absolute inset-1 rounded-full border border-line/40 border-b-cyan animate-spin [animation-direction:reverse]" />
      </div>
      <p className="text-xs text-muted font-medium tracking-wide">{label}…</p>
    </div>
  );
}

export function ErrorNote({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="rounded-xl border border-sev-critical/50 bg-sev-critical/10 p-4 backdrop-blur-sm">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-sev-critical/20 text-sev-critical font-bold text-xs">
          !
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-sev-critical">{message}</p>
          {onRetry && (
            <Button size="sm" variant="danger" className="mt-3" onClick={onRetry}>
              Try again
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

export function Table({
  headers,
  children,
}: {
  headers: string[];
  children: ReactNode;
}) {
  return (
    <div className="overflow-x-auto rounded-lg border border-line/60 bg-surface/20">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-line/80 bg-surface/60">
            {headers.map((header) => (
              <th key={header} className="eyebrow px-4 py-3 font-semibold text-muted/90">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-line/40 text-ink/90 font-normal">{children}</tbody>
      </table>
    </div>
  );
}
