import type { ButtonHTMLAttributes, ReactNode } from "react";

import { severityClasses } from "@/lib/utils/severity";

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
    <section className={`panel ${className}`}>
      {(title || action) && (
        <header className="flex items-center justify-between px-4 py-3 border-b border-line">
          {title && <h2 className="eyebrow">{title}</h2>}
          {action}
        </header>
      )}
      <div className="p-4">{children}</div>
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
    "inline-flex items-center justify-center gap-2 rounded-md border font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed";
  const sizes = size === "sm" ? "px-2.5 py-1 text-xs" : "px-3.5 py-2 text-sm";
  const variants = {
    primary: "bg-accent/15 border-accent/50 text-accent hover:bg-accent/25",
    ghost: "bg-raised border-line text-ink hover:border-muted",
    danger: "bg-sev-critical/10 border-sev-critical/40 text-sev-critical hover:bg-sev-critical/20",
  }[variant];

  return <button className={`${base} ${sizes} ${variants} ${className}`} {...props} />;
}

export function SeverityBadge({ severity }: { severity: string }) {
  return (
    <span
      className={`inline-block rounded border px-1.5 py-0.5 text-[0.6875rem] font-medium uppercase tracking-wide ${severityClasses(severity)}`}
    >
      {severity}
    </span>
  );
}

export function StatusChip({ status }: { status: string }) {
  const tone =
    status === "closed" || status === "dismissed"
      ? "text-muted border-line"
      : status === "action_executed"
        ? "text-ok border-ok/40"
        : "text-accent border-accent/40";
  return (
    <span className={`inline-block rounded border px-1.5 py-0.5 text-[0.6875rem] ${tone}`}>
      {status.replace(/_/g, " ")}
    </span>
  );
}

/**
 * The signature element: a risk score is never shown as a bare number. Hovering
 * reveals the factors that produced it, because an analyst who cannot audit the
 * score has no reason to trust it.
 */
export function RiskScore({
  score,
  factors,
}: {
  score: number;
  factors?: Record<string, number>;
}) {
  const hex = score >= 80 ? "#FF4D6D" : score >= 60 ? "#FF9F43" : score >= 35 ? "#FFD166" : "#4CC9F0";
  const entries = Object.entries(factors ?? {});

  return (
    <div className="group relative inline-flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-raised">
        <div
          className="h-full rounded-full"
          style={{ width: `${Math.min(score, 100)}%`, backgroundColor: hex }}
        />
      </div>
      <span className="data font-medium" style={{ color: hex }}>
        {score}
      </span>

      {entries.length > 0 && (
        <div className="pointer-events-none absolute left-0 top-6 z-20 hidden w-56 rounded-md border border-line bg-raised p-3 shadow-xl group-hover:block">
          <p className="eyebrow mb-2">How this score was built</p>
          <dl className="space-y-1">
            {entries.map(([key, value]) => (
              <div key={key} className="flex justify-between text-xs">
                <dt className="text-muted">{key.replace(/_/g, " ")}</dt>
                <dd className="data text-ink">{value}</dd>
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
    <div className="py-12 text-center">
      <p className="text-sm text-ink">{title}</p>
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </div>
  );
}

export function Loading({ label = "Loading" }: { label?: string }) {
  return <p className="py-10 text-center text-xs text-muted">{label}…</p>;
}

export function ErrorNote({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="rounded-md border border-sev-critical/40 bg-sev-critical/10 p-4">
      <p className="text-sm text-sev-critical">{message}</p>
      {onRetry && (
        <Button size="sm" className="mt-3" onClick={onRetry}>
          Try again
        </Button>
      )}
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
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-line">
            {headers.map((header) => (
              <th key={header} className="eyebrow pb-2 pr-4 font-medium">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-line/60">{children}</tbody>
      </table>
    </div>
  );
}
