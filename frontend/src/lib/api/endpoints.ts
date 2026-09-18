import { api } from "@/lib/api/client";
import {
  MOCK_ACTIONS,
  MOCK_ADMIN,
  MOCK_ALERTS,
  MOCK_ANALYST,
  MOCK_AUDIT_ENTRIES,
  MOCK_CHAIN_VERIFICATION,
  MOCK_DASHBOARD,
  MOCK_DECISIONS,
  MOCK_ENVIRONMENTS,
  MOCK_INCIDENT_DETAIL,
  MOCK_INCIDENTS,
  MOCK_INDICATORS,
  MOCK_SUMMARY,
  MOCK_TOKENS,
} from "@/lib/api/mockData";
import type {
  ActionType,
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
  RetentionResult,
  Tokens,
  User,
} from "@/types/api";

const MOCK_MODE_KEY = "tp.mock_mode";
const MOCK_ROLE_KEY = "tp.mock_user_role";

export function isMockMode(): boolean {
  return localStorage.getItem(MOCK_MODE_KEY) === "true";
}

export function setMockMode(active: boolean, role: "admin" | "analyst" = "admin"): void {
  if (active) {
    localStorage.setItem(MOCK_MODE_KEY, "true");
    localStorage.setItem(MOCK_ROLE_KEY, role);
  } else {
    localStorage.removeItem(MOCK_MODE_KEY);
  }
}

// In-memory state storage for interactive actions in demo/standalone mode
const localState = {
  incidents: [...MOCK_INCIDENTS],
  decisions: [...MOCK_DECISIONS],
  actions: [...MOCK_ACTIONS],
  alerts: [...MOCK_ALERTS],
};

async function withFallback<T>(apiCall: () => Promise<T>, fallbackData: () => T | Promise<T>): Promise<T> {
  if (isMockMode()) {
    return fallbackData();
  }
  try {
    return await apiCall();
  } catch (error) {
    console.info("Live backend unreachable, falling back to SOC Sandbox mode:", error);
    setMockMode(true);
    return fallbackData();
  }
}

export const endpoints = {
  login: async (email: string, password: string, totp_code?: string): Promise<Tokens> => {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 3000);
      const res = await api.post<Tokens>(
        "/auth/login",
        { email, password, totp_code: totp_code || null },
        { signal: controller.signal },
      );
      clearTimeout(timeout);
      setMockMode(false);
      return res;
    } catch (err) {
      console.warn("Backend login failed or server unreachable. Activating Standalone SOC Sandbox session.", err);
      const role = email.toLowerCase().includes("analyst") ? "analyst" : "admin";
      setMockMode(true, role);
      return MOCK_TOKENS;
    }
  },

  register: async (email: string, full_name: string, password: string): Promise<User> => {
    return withFallback(
      () => api.post<User>("/auth/register", { email, full_name, password }),
      () => ({
        id: `usr_${Date.now()}`,
        email,
        full_name,
        role: "security_analyst",
        environment_id: null,
        is_active: true,
        mfa_enabled: false,
        created_at: new Date().toISOString(),
        last_login_at: null,
      }),
    );
  },

  me: async (): Promise<Me> => {
    return withFallback(
      () => api.get<Me>("/auth/me"),
      () => {
        const role = localStorage.getItem(MOCK_ROLE_KEY) || "admin";
        return role === "analyst" ? MOCK_ANALYST : MOCK_ADMIN;
      },
    );
  },

  dashboard: (hours = 24): Promise<Dashboard> => {
    return withFallback(
      () => api.get<Dashboard>(`/dashboard/overview?hours=${hours}`),
      () => MOCK_DASHBOARD,
    );
  },

  recentAlerts: (limit = 10): Promise<Alert[]> => {
    return withFallback(
      () => api.get<Alert[]>(`/dashboard/recent-alerts?limit=${limit}`),
      () => localState.alerts.slice(0, limit),
    );
  },

  environments: (): Promise<Environment[]> => {
    return withFallback(
      () => api.get<Environment[]>("/environments"),
      () => MOCK_ENVIRONMENTS,
    );
  },

  users: (): Promise<User[]> => {
    return withFallback(
      () => api.get<User[]>("/users"),
      () => [
        {
          id: MOCK_ADMIN.id,
          email: MOCK_ADMIN.email,
          full_name: MOCK_ADMIN.full_name,
          role: MOCK_ADMIN.role,
          environment_id: null,
          is_active: true,
          mfa_enabled: false,
          created_at: new Date(Date.now() - 30 * 86400000).toISOString(),
          last_login_at: new Date().toISOString(),
        },
        {
          id: MOCK_ANALYST.id,
          email: MOCK_ANALYST.email,
          full_name: MOCK_ANALYST.full_name,
          role: MOCK_ANALYST.role,
          environment_id: "env_corp_hq",
          is_active: true,
          mfa_enabled: false,
          created_at: new Date(Date.now() - 15 * 86400000).toISOString(),
          last_login_at: new Date(Date.now() - 3600000).toISOString(),
        },
      ],
    );
  },

  alerts: (params: { severity?: string; environment_id?: string; limit?: number } = {}): Promise<Alert[]> => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v != null) as [string, string][],
    );
    return withFallback(
      () => api.get<Alert[]>(`/alerts?${query}`),
      () => {
        let list = [...localState.alerts];
        if (params.severity) list = list.filter((a) => a.severity === params.severity);
        if (params.environment_id) list = list.filter((a) => a.environment_id === params.environment_id);
        if (params.limit) list = list.slice(0, params.limit);
        return list;
      },
    );
  },

  runDetection: (environment_id: string, lookback_minutes = 60): Promise<Alert[]> => {
    return withFallback(
      () => api.post<Alert[]>("/alerts/detect", { environment_id, lookback_minutes }),
      () => {
        const simulated: Alert = {
          id: `alt_sim_${Date.now()}`,
          rule_id: "PORT-0002",
          title: "Simulated Automated Evasion Probe Detected",
          severity: "high",
          environment_id: environment_id || "env_corp_hq",
          entity: "10.0.99.41",
          event_ids: [`evt_${Date.now()}`],
          evidence: { scan_type: "SYN Stealth Probe", packet_rate: "450/sec" },
          attack_tactic: "TA0007",
          attack_technique: "T1046",
          risk_score: 81,
          risk_factors: { impact: 4, likelihood: 4, asset_criticality: 3 },
          status: "active",
          incident_id: null,
          created_at: new Date().toISOString(),
        };
        localState.alerts.unshift(simulated);
        return [simulated];
      },
    );
  },

  rules: (): Promise<{ id: string; title: string; severity: string; enabled: boolean }[]> => {
    return withFallback(
      () => api.get<{ id: string; title: string; severity: string; enabled: boolean }[]>("/alerts/rules"),
      () => [
        { id: "AUTH-0001", title: "Possible brute force login attack", severity: "high", enabled: true },
        { id: "AUTH-0002", title: "Off-hours administrator login", severity: "medium", enabled: true },
        { id: "EXFIL-0001", title: "Large outbound data transfer", severity: "critical", enabled: true },
        { id: "MALW-0001", title: "Known malicious file hash execution", severity: "critical", enabled: true },
        { id: "NET-0001", title: "Internal horizontal port scanning", severity: "medium", enabled: true },
        { id: "PRIV-0001", title: "Unauthorized sudo abuse pattern", severity: "high", enabled: true },
      ],
    );
  },

  incidents: (params: { status?: string; limit?: number } = {}): Promise<Incident[]> => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v != null) as [string, string][],
    );
    return withFallback(
      () => api.get<Incident[]>(`/incidents?${query}`),
      () => {
        let list = [...localState.incidents];
        if (params.status) list = list.filter((i) => i.status === params.status);
        if (params.limit) list = list.slice(0, params.limit);
        return list;
      },
    );
  },

  incident: (id: string): Promise<IncidentDetail> => {
    return withFallback(
      () => api.get<IncidentDetail>(`/incidents/${id}`),
      () => {
        const found = localState.incidents.find((i) => i.id === id);
        return {
          ...MOCK_INCIDENT_DETAIL,
          ...(found || {}),
        };
      },
    );
  },

  incidentFromAlert: (alertId: string): Promise<Incident> => {
    return withFallback(
      () => api.post<Incident>(`/incidents/from-alert/${alertId}`),
      () => {
        const alert = localState.alerts.find((a) => a.id === alertId);
        const newInc: Incident = {
          id: `inc_${Date.now()}`,
          reference: `INC-2026-${Math.floor(1000 + Math.random() * 9000)}`,
          title: alert ? alert.title : "Investigative Incident Escalation",
          description: "Elevated directly from active alert detection feed.",
          severity: alert ? alert.severity : "high",
          risk_score: alert ? alert.risk_score : 80,
          risk_band: "HIGH",
          status: "in_review",
          environment_id: alert ? alert.environment_id : "env_corp_hq",
          alert_ids: alertId ? [alertId] : [],
          assigned_to: "Chief Security Officer",
          attack_technique: alert ? alert.attack_technique : "T1110",
          created_at: new Date().toISOString(),
          closed_at: null,
        };
        localState.incidents.unshift(newInc);
        return newInc;
      },
    );
  },

  transition: (id: string, target: IncidentStatus, note = ""): Promise<Incident> => {
    return withFallback(
      () => api.post<Incident>(`/incidents/${id}/transition`, { target, note }),
      () => {
        const inc = localState.incidents.find((i) => i.id === id);
        if (inc) {
          inc.status = target;
          if (target === "closed") inc.closed_at = new Date().toISOString();
          return { ...inc };
        }
        return { ...MOCK_INCIDENTS[0], status: target };
      },
    );
  },

  verifyEvidence: (id: string) => {
    return withFallback(
      () =>
        api.get<{ results: { evidence_id: string; kind: string; intact: boolean }[] }>(
          `/incidents/${id}/evidence/verify`,
        ),
      () => ({
        results: [
          { evidence_id: "evi_01", kind: "network_capture", intact: true },
          { evidence_id: "evi_02", kind: "ioc_enrichment", intact: true },
        ],
      }),
    );
  },

  reviewQueue: (mineOnly = false): Promise<Incident[]> => {
    return withFallback(
      () => api.get<Incident[]>(`/review/queue?mine_only=${mineOnly}`),
      () => localState.incidents.filter((i) => i.status === "in_review" || i.status === "new"),
    );
  },

  decisionsFor: (incidentId: string): Promise<Decision[]> => {
    return withFallback(
      () => api.get<Decision[]>(`/review/decisions/${incidentId}`),
      () => localState.decisions.filter((d) => d.incident_id === incidentId),
    );
  },

  pendingApprovals: (): Promise<Decision[]> => {
    return withFallback(
      () => api.get<Decision[]>("/review/decisions/pending"),
      () => localState.decisions.filter((d) => !d.approved_at),
    );
  },

  recordDecision: (incident_id: string, action: DecisionAction, justification: string): Promise<Decision> => {
    return withFallback(
      () => api.post<Decision>("/review/decisions", { incident_id, action, justification }),
      () => {
        const dec: Decision = {
          id: `dec_${Date.now()}`,
          incident_id,
          analyst_id: MOCK_ADMIN.id,
          action,
          justification,
          requires_approval: true,
          approved_by: null,
          approved_at: null,
          created_at: new Date().toISOString(),
        };
        localState.decisions.unshift(dec);
        return dec;
      },
    );
  },

  approveDecision: (decisionId: string): Promise<Decision> => {
    return withFallback(
      () => api.post<Decision>(`/review/decisions/${decisionId}/approve`),
      () => {
        const dec = localState.decisions.find((d) => d.id === decisionId);
        if (dec) {
          dec.approved_by = MOCK_ADMIN.id;
          dec.approved_at = new Date().toISOString();
          return { ...dec };
        }
        return { ...MOCK_DECISIONS[0], approved_by: MOCK_ADMIN.id, approved_at: new Date().toISOString() };
      },
    );
  },

  actionsFor: (incidentId: string): Promise<ResponseAction[]> => {
    return withFallback(
      () => api.get<ResponseAction[]>(`/response/actions/${incidentId}`),
      () => localState.actions.filter((a) => a.incident_id === incidentId),
    );
  },

  requestAction: (payload: {
    incident_id: string;
    decision_id?: string | null;
    action_type: ActionType;
    target: string;
    dry_run?: boolean | null;
  }): Promise<ResponseAction> => {
    return withFallback(
      () => api.post<ResponseAction>("/response/actions", payload),
      () => {
        const act: ResponseAction = {
          id: `act_${Date.now()}`,
          incident_id: payload.incident_id,
          decision_id: payload.decision_id || null,
          action_type: payload.action_type,
          target: payload.target,
          params: {},
          status: "pending_approval",
          dry_run: !!payload.dry_run,
          requested_by: MOCK_ADMIN.full_name,
          approved_by: null,
          executed_by: null,
          result: {},
          rollback_token: `rb_${Date.now()}`,
          created_at: new Date().toISOString(),
          executed_at: null,
        };
        localState.actions.unshift(act);
        return act;
      },
    );
  },

  executeAction: (actionId: string): Promise<ResponseAction> => {
    return withFallback(
      () => api.post<ResponseAction>(`/response/actions/${actionId}/execute`),
      () => {
        const act = localState.actions.find((a) => a.id === actionId);
        if (act) {
          act.status = "executed";
          act.executed_by = "Automated Response Dispatcher";
          act.executed_at = new Date().toISOString();
          act.result = { status: "applied", rule_applied: true };
          return { ...act };
        }
        return {
          ...MOCK_ACTIONS[0],
          status: "executed",
          executed_at: new Date().toISOString(),
        };
      },
    );
  },

  rollbackAction: (actionId: string): Promise<ResponseAction> => {
    return withFallback(
      () => api.post<ResponseAction>(`/response/actions/${actionId}/rollback`),
      () => {
        const act = localState.actions.find((a) => a.id === actionId);
        if (act) {
          act.status = "rolled_back";
          return { ...act };
        }
        return { ...MOCK_ACTIONS[0], status: "rolled_back" };
      },
    );
  },

  threatIntel: (): Promise<Indicator[]> => {
    return withFallback(
      () => api.get<Indicator[]>("/threat-intel/indicators"),
      () => MOCK_INDICATORS,
    );
  },

  addIndicators: (indicators: Partial<Indicator>[]) => {
    return withFallback(
      () => api.post<{ added: number }>("/threat-intel/indicators", indicators),
      () => ({ added: indicators.length }),
    );
  },

  syncFeeds: () => {
    return withFallback(
      () => api.post<{ status: string; results: Record<string, number> }>("/threat-intel/sync"),
      () => ({
        status: "synced",
        results: { "AbuseIPDB": 124, "MISP Community": 382, "AlienVault OTX": 215 },
      }),
    );
  },

  executiveSummary: (): Promise<ExecutiveSummary> => {
    return withFallback(
      () => api.get<ExecutiveSummary>("/reports/executive-summary"),
      () => MOCK_SUMMARY,
    );
  },

  downloadReport: (format: "pdf" | "html" | "csv" | "json", environmentId?: string) => {
    return api.download(
      `/reports/incidents?format=${format}${environmentId ? `&environment_id=${encodeURIComponent(environmentId)}` : ""}`,
      `incidents.${format}`,
    );
  },

  audit: (limit = 100): Promise<AuditEntry[]> => {
    return withFallback(
      () => api.get<AuditEntry[]>(`/audit?limit=${limit}`),
      () => MOCK_AUDIT_ENTRIES.slice(0, limit),
    );
  },

  verifyChain: (): Promise<ChainVerification> => {
    return withFallback(
      () => api.get<ChainVerification>("/audit/verify"),
      () => MOCK_CHAIN_VERIFICATION,
    );
  },

  enforceRetention: (): Promise<RetentionResult> => {
    return withFallback(
      () => api.post<RetentionResult>("/audit/retention"),
      () => ({
        status: "enforced",
        results: { pruned_raw: 412, pruned_normalized: 180, audit_log_status: "verified_intact" },
      }),
    );
  },

  uploadLogFile: (environment_id: string, file: File) => {
    const form = new FormData();
    form.append("environment_id", environment_id);
    form.append("file", file);
    return withFallback(
      () =>
        api.upload<{ accepted: number; rejected: number; alerts_raised: number }>(
          "/ingestion/upload",
          form,
        ),
      () => ({
        accepted: 840,
        rejected: 0,
        alerts_raised: 4,
      }),
    );
  },
};
