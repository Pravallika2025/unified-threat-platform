/**
 * Mirrors backend app/core/security/permissions.py.
 *
 * This is a convenience for hiding controls the user cannot use — it is not a
 * security boundary. The server re-checks every permission on every request.
 */
export const PERMISSIONS = {
  ENV_MANAGE: "environment.manage",
  ENV_VIEW: "environment.view",
  USER_MANAGE: "user.manage",
  USER_VIEW: "user.view",
  SETTINGS_MANAGE: "settings.manage",
  DATA_UPLOAD: "data.upload",
  DATA_VIEW: "data.view",
  ALERT_VIEW: "alert.view",
  INCIDENT_VIEW: "incident.view",
  INCIDENT_INVESTIGATE: "incident.investigate",
  INCIDENT_ASSIGN: "incident.assign",
  DECISION_RECOMMEND: "decision.recommend",
  DECISION_APPROVE: "decision.approve",
  RESPONSE_EXECUTE: "response.execute",
  REPORT_GENERATE: "report.generate",
  REPORT_VIEW: "report.view",
  AUDIT_VIEW: "audit.view",
} as const;

export type PermissionKey = (typeof PERMISSIONS)[keyof typeof PERMISSIONS];
