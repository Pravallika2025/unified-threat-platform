/**
 * Mirrors the backend Pydantic schemas.
 *
 * Keep in sync by running: npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts
 * Until that is wired into CI, treat this file as the contract and update both sides together.
 */

export type Severity = "critical" | "high" | "medium" | "low" | "info";

export type Role = "super_admin" | "security_analyst" | "environment_user";

export type IncidentStatus =
  | "new"
  | "in_review"
  | "investigating"
  | "decided"
  | "action_executed"
  | "closed"
  | "dismissed";

export type DecisionAction =
  | "block_contain"
  | "monitor"
  | "dismiss_false_positive"
  | "escalate"
  | "archive_resolve";

export type ActionType =
  | "block_ip"
  | "block_port"
  | "block_url"
  | "isolate_host"
  | "disable_account"
  | "kill_process"
  | "monitor"
  | "notify_only";

export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface Me {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  environment_id: string | null;
  is_active: boolean;
  mfa_enabled: boolean;
  permissions: string[];
}

export interface Environment {
  id: string;
  name: string;
  type: string;
  description: string | null;
  status: "healthy" | "warning" | "critical" | "offline";
  is_active: boolean;
  authorized_sources: string[];
  created_at: string;
}

export interface Alert {
  id: string;
  rule_id: string;
  title: string;
  severity: Severity;
  environment_id: string;
  entity: string;
  event_ids: string[];
  evidence: Record<string, unknown>;
  attack_tactic: string | null;
  attack_technique: string | null;
  risk_score: number;
  risk_factors: Record<string, number>;
  status: string;
  incident_id: string | null;
  created_at: string;
}

export interface Incident {
  id: string;
  reference: string;
  title: string;
  description: string | null;
  severity: Severity;
  risk_score: number;
  risk_band: string;
  status: IncidentStatus;
  environment_id: string;
  alert_ids: string[];
  assigned_to: string | null;
  attack_technique: string | null;
  created_at: string;
  closed_at: string | null;
}

export interface Evidence {
  id: string;
  kind: string;
  content: Record<string, unknown>;
  content_hash: string;
  collected_by: string | null;
  collected_at: string;
}

export interface TimelineEntry {
  id: string;
  actor_id: string | null;
  action: string;
  detail: string;
  entry_metadata: Record<string, unknown>;
  created_at: string;
}

export interface IncidentDetail extends Incident {
  evidence: Evidence[];
  timeline: TimelineEntry[];
}

export interface Decision {
  id: string;
  incident_id: string;
  analyst_id: string;
  action: DecisionAction;
  justification: string;
  requires_approval: boolean;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
}

export interface ResponseAction {
  id: string;
  incident_id: string;
  decision_id: string | null;
  action_type: ActionType;
  target: string;
  params: Record<string, unknown>;
  status: string;
  dry_run: boolean;
  requested_by: string;
  approved_by: string | null;
  executed_by: string | null;
  result: Record<string, unknown>;
  rollback_token?: string | null;
  created_at: string;
  executed_at: string | null;
}

export interface AuditEntry {
  id: string;
  sequence: number;
  actor_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  details: Record<string, unknown>;
  entry_hash: string;
  created_at: string;
}

export interface ChainVerification {
  valid: boolean;
  checked: number;
  broken_at: string | null;
  reason: string | null;
}

export interface Dashboard {
  kpis: {
    total_events: number;
    threats_detected: number;
    threats_last_24h: number;
    threats_trend_pct: number;
    high_risk: number;
    under_review: number;
    blocked_contained: number;
    open_incidents: number;
  };
  threats_over_time: { time: string; high: number; medium: number; low: number }[];
  severity_distribution: { label: string; count: number; percent: number }[];
  top_sources: { entity: string; count: number; severity: string }[];
  environment_status: {
    id: string;
    name: string;
    type: string;
    status: string;
    alerts_last_hour: number;
    high_severity: number;
  }[];
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  environment_id: string | null;
  is_active: boolean;
  mfa_enabled: boolean;
  created_at: string;
  last_login_at: string | null;
}

export interface Indicator {
  id: string;
  value: string;
  type: string;
  source: string;
  confidence: number;
  severity: Severity;
  description: string | null;
  first_seen: string;
  last_seen: string;
}

export interface ExecutiveSummary {
  generated_for: string;
  kpis: {
    total_events?: number;
    threats_detected?: number;
    high_risk?: number;
    open_incidents?: number;
    blocked_contained?: number;
    [key: string]: unknown;
  };
  note: string;
}

export interface RetentionResult {
  status: string;
  results: {
    pruned_raw: number;
    pruned_normalized: number;
    audit_log_status: string;
  };
}

