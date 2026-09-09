import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  Button,
  EmptyState,
  ErrorNote,
  Loading,
  Panel,
  RiskScore,
  SeverityBadge,
  StatusChip,
} from "@/components/ui";
import { Can } from "@/lib/rbac/Can";
import { PERMISSIONS } from "@/lib/rbac/permissions";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";
import { formatDateTime, humanize } from "@/lib/utils/format";
import type { DecisionAction, IncidentStatus } from "@/types/api";

/** Mirrors the backend state machine so the analyst always knows what comes next. */
const FLOW: IncidentStatus[] = [
  "new",
  "in_review",
  "investigating",
  "decided",
  "action_executed",
  "closed",
];

const DECISIONS: { value: DecisionAction; label: string; destructive?: boolean }[] = [
  { value: "block_contain", label: "Block / contain", destructive: true },
  { value: "monitor", label: "Keep monitoring" },
  { value: "escalate", label: "Escalate" },
  { value: "dismiss_false_positive", label: "Dismiss as false positive" },
  { value: "archive_resolve", label: "Archive / resolve" },
];

export function IncidentDetailPage() {
  const { id = "" } = useParams();
  const incident = useApi(() => endpoints.incident(id), [id]);
  const decisions = useApi(() => endpoints.decisionsFor(id), [id]);
  const actions = useApi(() => endpoints.actionsFor(id), [id]);

  const [action, setAction] = useState<DecisionAction>("monitor");
  const [justification, setJustification] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<{ tone: "ok" | "error"; text: string } | null>(null);
  const [integrity, setIntegrity] = useState<string | null>(null);

  if (incident.loading && !incident.data) return <Loading label="Loading incident" />;
  if (incident.error) return <ErrorNote message={incident.error} onRetry={incident.reload} />;
  if (!incident.data) return null;

  const data = incident.data;
  const currentStep = FLOW.indexOf(data.status);
  const selected = DECISIONS.find((d) => d.value === action);

  async function submitDecision() {
    setBusy(true);
    setNotice(null);
    try {
      const decision = await endpoints.recordDecision(id, action, justification);
      setJustification("");
      setNotice({
        tone: "ok",
        text: decision.requires_approval
          ? "Decision recorded. It needs approval from a second authorised user before it can be carried out."
          : "Decision recorded.",
      });
      await Promise.all([decisions.reload(), incident.reload()]);
    } catch (error) {
      setNotice({ tone: "error", text: error instanceof Error ? error.message : "Could not record the decision" });
    } finally {
      setBusy(false);
    }
  }

  async function approve(decisionId: string) {
    try {
      await endpoints.approveDecision(decisionId);
      setNotice({ tone: "ok", text: "Decision approved." });
      await decisions.reload();
    } catch (error) {
      setNotice({ tone: "error", text: error instanceof Error ? error.message : "Approval failed" });
    }
  }

  async function checkEvidence() {
    const result = await endpoints.verifyEvidence(id);
    const broken = result.results.filter((item) => !item.intact);
    setIntegrity(
      broken.length === 0
        ? `All ${result.results.length} evidence items verified intact.`
        : `${broken.length} of ${result.results.length} evidence items failed verification.`,
    );
  }

  async function executeAction(actionId: string) {
    try {
      await endpoints.executeAction(actionId);
      setNotice({ tone: "ok", text: "Response action executed successfully." });
      await Promise.all([actions.reload(), incident.reload()]);
    } catch (error) {
      setNotice({ tone: "error", text: error instanceof Error ? error.message : "Action execution failed" });
    }
  }

  async function rollbackAction(actionId: string) {
    try {
      await endpoints.rollbackAction(actionId);
      setNotice({ tone: "ok", text: "Response action rolled back successfully." });
      await Promise.all([actions.reload(), incident.reload()]);
    } catch (error) {
      setNotice({ tone: "error", text: error instanceof Error ? error.message : "Action rollback failed" });
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link to="/incidents" className="eyebrow hover:text-ink">
            ← All incidents
          </Link>
          <h1 className="mt-1 text-lg font-semibold tracking-tight">{data.title}</h1>
          <div className="mt-1.5 flex flex-wrap items-center gap-2">
            <span className="data text-muted">{data.reference}</span>
            <SeverityBadge severity={data.severity} />
            <StatusChip status={data.status} />
            {data.attack_technique && (
              <span className="data rounded border border-line px-1.5 py-0.5 text-xs text-muted">
                ATT&amp;CK {data.attack_technique}
              </span>
            )}
          </div>
        </div>
        <RiskScore score={data.risk_score} />
      </div>

      {/* The decision flow, drawn from the same states the server enforces. */}
      <div className="panel px-4 py-3">
        <ol className="flex flex-wrap items-center gap-1.5">
          {FLOW.map((step, index) => {
            const done = index < currentStep;
            const active = index === currentStep;
            return (
              <li key={step} className="flex items-center gap-1.5">
                <span
                  className={`rounded border px-2 py-0.5 text-[0.6875rem] ${
                    active
                      ? "border-accent/50 bg-accent/15 text-accent"
                      : done
                        ? "border-ok/40 text-ok"
                        : "border-line text-faint"
                  }`}
                >
                  {humanize(step)}
                </span>
                {index < FLOW.length - 1 && <span className="text-faint">→</span>}
              </li>
            );
          })}
        </ol>
      </div>

      {notice && (
        <p
          className={`rounded-md border px-3 py-2 text-sm ${
            notice.tone === "ok"
              ? "border-ok/40 bg-ok/10 text-ok"
              : "border-sev-critical/40 bg-sev-critical/10 text-sev-critical"
          }`}
        >
          {notice.text}
        </p>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <Panel
            title="Evidence"
            action={
              <Button size="sm" onClick={checkEvidence}>
                Verify integrity
              </Button>
            }
          >
            {integrity && <p className="mb-3 text-xs text-ok">{integrity}</p>}
            {data.evidence.length === 0 ? (
              <EmptyState title="No evidence attached" />
            ) : (
              <ul className="space-y-3">
                {data.evidence.map((item) => (
                  <li key={item.id} className="rounded-md border border-line bg-raised p-3">
                    <div className="mb-2 flex items-center justify-between">
                      <span className="eyebrow">{item.kind}</span>
                      <span className="data text-faint" title="SHA-256 of the content">
                        {item.content_hash.slice(0, 16)}…
                      </span>
                    </div>
                    <pre className="data overflow-x-auto whitespace-pre-wrap break-words text-muted">
                      {JSON.stringify(item.content, null, 2)}
                    </pre>
                  </li>
                ))}
              </ul>
            )}
          </Panel>

          <Panel title="Timeline">
            {data.timeline.length === 0 ? (
              <EmptyState title="Nothing recorded yet" />
            ) : (
              <ol className="space-y-3">
                {data.timeline.map((entry) => (
                  <li key={entry.id} className="border-l border-line pl-3">
                    <p className="text-sm text-ink">{entry.detail}</p>
                    <p className="eyebrow mt-0.5">
                      {humanize(entry.action)} · {formatDateTime(entry.created_at)}
                    </p>
                  </li>
                ))}
              </ol>
            )}
          </Panel>
        </div>

        <div className="space-y-4">
          <Can
            do={PERMISSIONS.DECISION_RECOMMEND}
            fallback={
              <Panel title="Decision">
                <p className="text-xs text-muted">
                  Your role can view this incident but not decide on it.
                </p>
              </Panel>
            }
          >
            <Panel title="Record a decision">
              <label htmlFor="action" className="eyebrow mb-1.5 block">
                Action
              </label>
              <select
                id="action"
                value={action}
                onChange={(event) => setAction(event.target.value as DecisionAction)}
                className="w-full rounded-md border border-line bg-raised px-3 py-2 text-sm"
              >
                {DECISIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>

              {selected?.destructive && (
                <p className="mt-2 rounded border border-sev-medium/40 bg-sev-medium/10 px-2.5 py-1.5 text-xs text-sev-medium">
                  This is a destructive action. A second authorised user must approve it before it
                  can be carried out.
                </p>
              )}

              <label htmlFor="justification" className="eyebrow mb-1.5 mt-3 block">
                Justification
              </label>
              <textarea
                id="justification"
                rows={4}
                value={justification}
                onChange={(event) => setJustification(event.target.value)}
                placeholder="Why this action, based on what evidence"
                className="w-full rounded-md border border-line bg-raised px-3 py-2 text-sm placeholder:text-faint"
              />
              <p className="mt-1 text-xs text-faint">
                {justification.trim().length}/20 characters minimum. This becomes part of the
                permanent record.
              </p>

              <Button
                variant="primary"
                className="mt-3 w-full"
                disabled={busy || justification.trim().length < 20}
                onClick={submitDecision}
              >
                {busy ? "Recording…" : "Record decision"}
              </Button>
            </Panel>
          </Can>

          <Panel title="Decisions">
            {decisions.data && decisions.data.length > 0 ? (
              <ul className="space-y-3">
                {decisions.data.map((decision) => (
                  <li key={decision.id} className="rounded-md border border-line bg-raised p-3">
                    <p className="text-sm text-ink">{humanize(decision.action)}</p>
                    <p className="mt-1 text-xs text-muted">{decision.justification}</p>
                    <p className="eyebrow mt-2">
                      {decision.approved_by
                        ? "Approved"
                        : decision.requires_approval
                          ? "Awaiting approval"
                          : "No approval needed"}
                    </p>
                    {decision.requires_approval && !decision.approved_by && (
                      <Can do={PERMISSIONS.DECISION_APPROVE}>
                        <Button size="sm" className="mt-2" onClick={() => approve(decision.id)}>
                          Approve
                        </Button>
                      </Can>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState title="No decisions recorded" />
            )}
          </Panel>

          <Panel title="Response actions">
            {actions.data && actions.data.length > 0 ? (
              <ul className="space-y-2">
                {actions.data.map((item) => (
                  <li key={item.id} className="rounded-md border border-line bg-raised p-3 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-ink">{humanize(item.action_type)}</span>
                      <span className="text-muted">{humanize(item.status)}</span>
                    </div>
                    <p className="data mt-1 text-muted">{item.target}</p>
                    {item.dry_run && (
                      <p className="mt-1 text-sev-low">Simulation only — nothing was changed.</p>
                    )}
                    <div className="mt-2 flex items-center gap-2">
                      {item.status === "pending_approval" && (
                        <Can do={PERMISSIONS.RESPONSE_EXECUTE}>
                          <Button size="sm" variant="primary" onClick={() => executeAction(item.id)}>
                            Execute now
                          </Button>
                        </Can>
                      )}
                      {item.status === "executed" && item.rollback_token && (
                        <Can do={PERMISSIONS.RESPONSE_EXECUTE}>
                          <Button size="sm" variant="danger" onClick={() => rollbackAction(item.id)}>
                            Rollback action
                          </Button>
                        </Can>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState title="No actions requested" />
            )}
          </Panel>
        </div>
      </div>
    </div>
  );
}
