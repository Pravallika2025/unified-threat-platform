import type { Severity } from "@/types/api";

/** One source of truth for severity colour, used by badges, borders and charts alike. */
export const SEVERITY_HEX: Record<Severity, string> = {
  critical: "#FF4D6D",
  high: "#FF9F43",
  medium: "#FFD166",
  low: "#4CC9F0",
  info: "#7C8DA0",
};

export const SEVERITY_ORDER: Severity[] = ["critical", "high", "medium", "low", "info"];

export function severityClasses(severity: string): string {
  switch (severity) {
    case "critical":
      return "text-sev-critical border-sev-critical/40 bg-sev-critical/10";
    case "high":
      return "text-sev-high border-sev-high/40 bg-sev-high/10";
    case "medium":
      return "text-sev-medium border-sev-medium/40 bg-sev-medium/10";
    case "low":
      return "text-sev-low border-sev-low/40 bg-sev-low/10";
    default:
      return "text-muted border-line bg-raised";
  }
}

export function riskBand(score: number): { label: string; hex: string } {
  if (score >= 80) return { label: "critical", hex: SEVERITY_HEX.critical };
  if (score >= 60) return { label: "high", hex: SEVERITY_HEX.high };
  if (score >= 35) return { label: "medium", hex: SEVERITY_HEX.medium };
  return { label: "low", hex: SEVERITY_HEX.low };
}

export function environmentStatusClasses(status: string): string {
  switch (status) {
    case "critical":
      return "text-sev-critical";
    case "warning":
      return "text-sev-medium";
    case "offline":
      return "text-muted";
    default:
      return "text-ok";
  }
}
