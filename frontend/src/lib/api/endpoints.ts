import { api } from "@/lib/api/client";
import type {
  Alert,
  AuditEntry,
  ChainVerification,
  Dashboard,
  Decision,
  DecisionAction,
  Environment,
  ExecutiveSummary,
  Incident,
  IncidentDetail,
  IncidentStatus,
  Indicator,
  Me,
  ResponseAction,
  ActionType,
  RetentionResult,
  Tokens,
  User,
} from "@/types/api";

export const endpoints = {
  login: (email: string, password: string, totp_code?: string) =>
    api.post<Tokens>("/auth/login", { email, password, totp_code: totp_code || null }),
  register: (email: string, full_name: string, password: string) =>
    api.post<User>("/auth/register", { email, full_name, password }),
  me: () => api.get<Me>("/auth/me"),


  dashboard: (hours = 24) => api.get<Dashboard>(`/dashboard/overview?hours=${hours}`),
  recentAlerts: (limit = 10) => api.get<Alert[]>(`/dashboard/recent-alerts?limit=${limit}`),

  environments: () => api.get<Environment[]>("/environments"),
  users: () => api.get<User[]>("/users"),

  alerts: (params: { severity?: string; environment_id?: string; limit?: number } = {}) => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v != null) as [string, string][],
    );
    return api.get<Alert[]>(`/alerts?${query}`);
  },
  runDetection: (environment_id: string, lookback_minutes = 60) =>
    api.post<Alert[]>("/alerts/detect", { environment_id, lookback_minutes }),
  rules: () => api.get<{ id: string; title: string; severity: string; enabled: boolean }[]>("/alerts/rules"),

  incidents: (params: { status?: string; limit?: number } = {}) => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v != null) as [string, string][],
    );
    return api.get<Incident[]>(`/incidents?${query}`);
  },
  incident: (id: string) => api.get<IncidentDetail>(`/incidents/${id}`),
  incidentFromAlert: (alertId: string) => api.post<Incident>(`/incidents/from-alert/${alertId}`),
  transition: (id: string, target: IncidentStatus, note = "") =>
    api.post<Incident>(`/incidents/${id}/transition`, { target, note }),
  verifyEvidence: (id: string) =>
    api.get<{ results: { evidence_id: string; kind: string; intact: boolean }[] }>(
      `/incidents/${id}/evidence/verify`,
    ),

  reviewQueue: (mineOnly = false) => api.get<Incident[]>(`/review/queue?mine_only=${mineOnly}`),
  decisionsFor: (incidentId: string) => api.get<Decision[]>(`/review/decisions/${incidentId}`),
  pendingApprovals: () => api.get<Decision[]>("/review/decisions/pending"),
  recordDecision: (incident_id: string, action: DecisionAction, justification: string) =>
    api.post<Decision>("/review/decisions", { incident_id, action, justification }),
  approveDecision: (decisionId: string) =>
    api.post<Decision>(`/review/decisions/${decisionId}/approve`),

  actionsFor: (incidentId: string) => api.get<ResponseAction[]>(`/response/actions/${incidentId}`),
  requestAction: (payload: {
    incident_id: string;
    decision_id?: string | null;
    action_type: ActionType;
    target: string;
    dry_run?: boolean | null;
  }) => api.post<ResponseAction>("/response/actions", payload),
  executeAction: (actionId: string) =>
    api.post<ResponseAction>(`/response/actions/${actionId}/execute`),
  rollbackAction: (actionId: string) =>
    api.post<ResponseAction>(`/response/actions/${actionId}/rollback`),

  threatIntel: () => api.get<Indicator[]>("/threat-intel/indicators"),
  addIndicators: (indicators: Partial<Indicator>[]) =>
    api.post<{ added: number }>("/threat-intel/indicators", indicators),
  syncFeeds: () => api.post<{ status: string; results: Record<string, number> }>("/threat-intel/sync"),

  executiveSummary: () => api.get<ExecutiveSummary>("/reports/executive-summary"),
  downloadReport: (format: "pdf" | "html" | "csv" | "json", environmentId?: string) =>
    api.download(
      `/reports/incidents?format=${format}${environmentId ? `&environment_id=${encodeURIComponent(environmentId)}` : ""}`,
      `incidents.${format}`,
    ),

  audit: (limit = 100) => api.get<AuditEntry[]>(`/audit?limit=${limit}`),
  verifyChain: () => api.get<ChainVerification>("/audit/verify"),
  enforceRetention: () => api.post<RetentionResult>("/audit/retention"),

  uploadLogFile: (environment_id: string, file: File) => {
    const form = new FormData();
    form.append("environment_id", environment_id);
    form.append("file", file);
    return api.upload<{ accepted: number; rejected: number; alerts_raised: number }>(
      "/ingestion/upload",
      form,
    );
  },
};
