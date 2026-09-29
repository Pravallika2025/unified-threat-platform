import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { Button, EmptyState, ErrorNote, Loading, Panel, RiskScore, SeverityBadge, Table } from "@/components/ui";
import { Can } from "@/lib/rbac/Can";
import { PERMISSIONS } from "@/lib/rbac/permissions";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";
import { relativeTime, truncate } from "@/lib/utils/format";
import type { SmtpConfig } from "@/types/api";

export function AlertsPage() {
  const alerts = useApi(() => endpoints.alerts({ limit: 100 }), []);
  const environments = useApi(() => endpoints.environments(), []);
  const [running, setRunning] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  // SMTP Email Alerts Credentials State
  const [showCredsModal, setShowCredsModal] = useState(false);
  const [smtpConfig, setSmtpConfig] = useState<SmtpConfig | null>(null);
  const [smtpHost, setSmtpHost] = useState("smtp.gmail.com");
  const [smtpPort, setSmtpPort] = useState(587);
  const [smtpUser, setSmtpUser] = useState("");
  const [smtpPassword, setSmtpPassword] = useState("");
  const [fromAddr, setFromAddr] = useState("alerts@threatplatform.dev");
  const [toAddr, setToAddr] = useState("soc-admin@college.edu");
  const [showPassword, setShowPassword] = useState(false);
  const [savingCreds, setSavingCreds] = useState(false);
  const [testingCreds, setTestingCreds] = useState(false);
  const [modalFeedback, setModalFeedback] = useState<{ type: "success" | "error" | "info"; text: string } | null>(null);

  useEffect(() => {
    endpoints.getSmtpConfig().then((cfg) => {
      setSmtpConfig(cfg);
      if (cfg.smtp_host) setSmtpHost(cfg.smtp_host);
      if (cfg.smtp_port) setSmtpPort(cfg.smtp_port);
      if (cfg.smtp_user) setSmtpUser(cfg.smtp_user);
      if (cfg.from_addr) setFromAddr(cfg.from_addr);
      if (cfg.to_addr) setToAddr(cfg.to_addr);
    }).catch(() => {});
  }, []);

  async function runDetection() {
    const environmentId = environments.data?.[0]?.id;
    if (!environmentId) return;
    setRunning(true);
    try {
      const found = await endpoints.runDetection(environmentId, 60);
      setNotice(
        found.length === 0
          ? "Detection ran and found nothing new in the last hour."
          : `Detection produced ${found.length} new alert${found.length === 1 ? "" : "s"}.`,
      );
      await alerts.reload();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Detection failed");
    } finally {
      setRunning(false);
    }
  }

  function applyPreset(preset: "gmail" | "outlook" | "college") {
    setModalFeedback(null);
    if (preset === "gmail") {
      setSmtpHost("smtp.gmail.com");
      setSmtpPort(587);
      setFromAddr(smtpUser || "your-email@gmail.com");
      setModalFeedback({
        type: "info",
        text: "Gmail preset applied. Use a 16-character Google App Password (not your standard password).",
      });
    } else if (preset === "outlook") {
      setSmtpHost("smtp.office365.com");
      setSmtpPort(587);
      setFromAddr(smtpUser || "your-email@outlook.com");
      setModalFeedback({
        type: "info",
        text: "Office 365 / Outlook preset applied. Port 587 with STARTTLS.",
      });
    } else {
      setSmtpHost("mail.college.edu");
      setSmtpPort(587);
      setFromAddr("security-alerts@college.edu");
      setToAddr("hod-cse@college.edu");
      setModalFeedback({
        type: "info",
        text: "College institutional mail relay preset applied.",
      });
    }
  }

  async function handleSaveCredentials(e: React.FormEvent) {
    e.preventDefault();
    setSavingCreds(true);
    setModalFeedback(null);
    try {
      const res = await endpoints.updateSmtpConfig({
        smtp_host: smtpHost,
        smtp_port: Number(smtpPort),
        smtp_user: smtpUser,
        smtp_password: smtpPassword,
        from_addr: fromAddr,
        to_addr: toAddr,
      });
      setSmtpConfig(res.config);
      setModalFeedback({
        type: "success",
        text: `✓ SMTP Credentials Saved! Real-time alerts for High & Critical threats will dispatch to ${toAddr}.`,
      });
    } catch (err) {
      setModalFeedback({
        type: "error",
        text: err instanceof Error ? err.message : "Failed to update SMTP credentials",
      });
    } finally {
      setSavingCreds(false);
    }
  }

  async function handleSendTestEmail() {
    setTestingCreds(true);
    setModalFeedback(null);
    try {
      const res = await endpoints.testSmtpAlert(toAddr);
      if (res.success) {
        setModalFeedback({
          type: "success",
          text: `✓ ${res.message}`,
        });
      } else {
        setModalFeedback({
          type: "error",
          text: `✗ ${res.message}`,
        });
      }
    } catch (err) {
      setModalFeedback({
        type: "error",
        text: err instanceof Error ? err.message : "Failed to dispatch test email",
      });
    } finally {
      setTestingCreds(false);
    }
  }

  return (
    <>
      <Panel
        title="Threat Alerts & Notifications"
        action={
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                setShowCredsModal(true);
                setModalFeedback(null);
              }}
              className="border-line/80 hover:border-cyan text-xs"
            >
              📧 Add / Edit SMTP Credentials
            </Button>
            <Can do={PERMISSIONS.INCIDENT_INVESTIGATE}>
              <Button size="sm" onClick={runDetection} disabled={running}>
                {running ? "Running…" : "Run detection now"}
              </Button>
            </Can>
          </div>
        }
      >
        {/* Real-time SMTP Status Bar */}
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2 rounded-xl border border-line/70 bg-raised/60 px-4 py-2.5 text-xs">
          <div className="flex items-center gap-2">
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                smtpConfig?.is_configured ? "bg-ok animate-pulse" : "bg-warning"
              }`}
            />
            <span className="font-semibold text-white">
              Real-Time Email Dispatch:
            </span>
            <span className="font-mono text-muted">
              {smtpConfig?.is_configured ? (
                <span className="text-ok">
                  Active (Host: {smtpConfig.smtp_host} → Recipient: {smtpConfig.to_addr})
                </span>
              ) : (
                <span className="text-warning">
                  Audit / Mock Mode (Configure SMTP to enable live inbox alerts)
                </span>
              )}
            </span>
          </div>

          <button
            type="button"
            onClick={() => {
              setShowCredsModal(true);
              setModalFeedback(null);
            }}
            className="font-mono text-[0.6875rem] text-cyan hover:underline cursor-pointer"
          >
            [ Configure Credentials & Test Alert ]
          </button>
        </div>

        {notice && <p className="mb-3 text-xs text-muted">{notice}</p>}

        {alerts.loading && !alerts.data ? (
          <Loading label="Loading alerts" />
        ) : alerts.error ? (
          <ErrorNote message={alerts.error} onRetry={alerts.reload} />
        ) : !alerts.data || alerts.data.length === 0 ? (
          <EmptyState
            title="No alerts"
            hint="Ingest logs, then run detection to evaluate them against the rule set."
          />
        ) : (
          <Table headers={["Severity", "Rule", "Detection", "Entity", "Risk", "ATT&CK", "Seen"]}>
            {alerts.data.map((alert) => (
              <tr key={alert.id}>
                <td className="py-2.5 pr-4">
                  <SeverityBadge severity={alert.severity} />
                </td>
                <td className="data py-2.5 pr-4 text-muted">{alert.rule_id}</td>
                <td className="py-2.5 pr-4">
                  {alert.incident_id ? (
                    <Link to={`/incidents/${alert.incident_id}`} className="hover:text-accent">
                      {truncate(alert.title, 44)}
                    </Link>
                  ) : (
                    truncate(alert.title, 44)
                  )}
                </td>
                <td className="data py-2.5 pr-4 text-muted">{truncate(alert.entity, 26)}</td>
                <td className="py-2.5 pr-4">
                  <RiskScore score={alert.risk_score} factors={alert.risk_factors} />
                </td>
                <td className="data py-2.5 pr-4 text-faint">{alert.attack_technique ?? "—"}</td>
                <td className="py-2.5 text-xs text-muted">{relativeTime(alert.created_at)}</td>
              </tr>
            ))}
          </Table>
        )}
      </Panel>

      {/* SMTP Email Credentials Modal Dialog */}
      {showCredsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-lg rounded-2xl border border-line bg-panel p-6 shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-line/70 mb-4">
              <div>
                <div className="inline-flex items-center gap-1.5 text-cyan text-xs font-mono font-bold uppercase tracking-wider mb-1">
                  <span className="h-2 w-2 rounded-full bg-cyan animate-ping" />
                  Real-Time Notification Dispatch
                </div>
                <h3 className="text-lg font-bold text-white">
                  Add SMTP Email Credentials
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setShowCredsModal(false)}
                className="text-muted hover:text-white text-lg p-1"
                aria-label="Close"
              >
                ✕
              </button>
            </div>

            {/* Quick Presets */}
            <div className="mb-4">
              <label className="text-[0.6875rem] font-mono uppercase text-muted block mb-1.5">
                Quick Relay Presets:
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => applyPreset("gmail")}
                  className="rounded-lg border border-line/80 bg-raised/70 py-1.5 px-2 text-xs font-semibold text-ink hover:border-cyan hover:bg-elevated transition-colors"
                >
                  ⚡ Gmail SMTP
                </button>
                <button
                  type="button"
                  onClick={() => applyPreset("outlook")}
                  className="rounded-lg border border-line/80 bg-raised/70 py-1.5 px-2 text-xs font-semibold text-ink hover:border-cyan hover:bg-elevated transition-colors"
                >
                  🏢 Office 365
                </button>
                <button
                  type="button"
                  onClick={() => applyPreset("college")}
                  className="rounded-lg border border-line/80 bg-raised/70 py-1.5 px-2 text-xs font-semibold text-ink hover:border-cyan hover:bg-elevated transition-colors"
                >
                  🎓 College Server
                </button>
              </div>
            </div>

            {/* Feedback alert */}
            {modalFeedback && (
              <div
                className={`mb-4 p-3 rounded-lg border text-xs font-mono ${
                  modalFeedback.type === "success"
                    ? "border-ok/40 bg-ok/10 text-ok"
                    : modalFeedback.type === "error"
                    ? "border-sev-critical/40 bg-sev-critical/10 text-sev-critical"
                    : "border-cyan/40 bg-cyan/10 text-cyan"
                }`}
              >
                {modalFeedback.text}
              </div>
            )}

            <form onSubmit={handleSaveCredentials} className="space-y-3.5">
              <div className="grid grid-cols-3 gap-3">
                <div className="col-span-2">
                  <label className="text-xs text-muted block mb-1">
                    SMTP Server Host
                  </label>
                  <input
                    type="text"
                    required
                    value={smtpHost}
                    onChange={(e) => setSmtpHost(e.target.value)}
                    placeholder="smtp.gmail.com"
                    className="w-full rounded-lg border border-line bg-raised px-3 py-1.5 text-xs text-ink font-mono focus:border-cyan focus:outline-none"
                  />
                </div>
                <div>
                  <label className="text-xs text-muted block mb-1">
                    Port
                  </label>
                  <input
                    type="number"
                    required
                    value={smtpPort}
                    onChange={(e) => setSmtpPort(Number(e.target.value))}
                    placeholder="587"
                    className="w-full rounded-lg border border-line bg-raised px-3 py-1.5 text-xs text-ink font-mono focus:border-cyan focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs text-muted block mb-1">
                  SMTP Username / Email Address
                </label>
                <input
                  type="text"
                  required
                  value={smtpUser}
                  onChange={(e) => setSmtpUser(e.target.value)}
                  placeholder="analyst@yourcollege.edu or gmail address"
                  className="w-full rounded-lg border border-line bg-raised px-3 py-1.5 text-xs text-ink font-mono focus:border-cyan focus:outline-none"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs text-muted">
                    Password / App Password
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-[0.6875rem] text-cyan hover:underline"
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={smtpPassword}
                  onChange={(e) => setSmtpPassword(e.target.value)}
                  placeholder="16-character Google App Password or password"
                  className="w-full rounded-lg border border-line bg-raised px-3 py-1.5 text-xs text-ink font-mono focus:border-cyan focus:outline-none"
                />
                <p className="mt-1 text-[0.625rem] text-faint">
                  For Gmail: generate at{" "}
                  <a
                    href="https://myaccount.google.com/apppasswords"
                    target="_blank"
                    rel="noreferrer"
                    className="text-cyan underline"
                  >
                    Google App Passwords
                  </a>{" "}
                  (requires 2FA).
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-muted block mb-1">
                    From Address
                  </label>
                  <input
                    type="email"
                    value={fromAddr}
                    onChange={(e) => setFromAddr(e.target.value)}
                    placeholder="alerts@threatplatform.dev"
                    className="w-full rounded-lg border border-line bg-raised px-3 py-1.5 text-xs text-ink font-mono focus:border-cyan focus:outline-none"
                  />
                </div>
                <div>
                  <label className="text-xs text-muted block mb-1">
                    Alert Recipient (To)
                  </label>
                  <input
                    type="email"
                    required
                    value={toAddr}
                    onChange={(e) => setToAddr(e.target.value)}
                    placeholder="hod@college.edu"
                    className="w-full rounded-lg border border-line bg-raised px-3 py-1.5 text-xs text-ink font-mono focus:border-cyan focus:outline-none"
                  />
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-line/70 flex items-center justify-between gap-3">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  disabled={testingCreds}
                  onClick={handleSendTestEmail}
                  className="text-xs border-cyan/40 text-cyan hover:bg-cyan/10 cursor-pointer"
                >
                  {testingCreds ? "Dispatching…" : "⚡ Send Test Alert Email"}
                </Button>

                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowCredsModal(false)}
                    className="text-xs"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    size="sm"
                    disabled={savingCreds}
                    className="text-xs shadow-glow-accent cursor-pointer"
                  >
                    {savingCreds ? "Saving…" : "Save Credentials"}
                  </Button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
