import { useState } from "react";

import { Button, EmptyState, ErrorNote, Loading, Panel, Table } from "@/components/ui";
import { Can } from "@/lib/rbac/Can";
import { PERMISSIONS } from "@/lib/rbac/permissions";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";
import { formatDateTime, humanize } from "@/lib/utils/format";
import type { Role, User } from "@/types/api";

export function UsersPage() {
  const { data, error, loading, reload } = useApi(() => endpoints.users(), []);
  const [actionNotice, setActionNotice] = useState<string | null>(null);
  const [busyUserId, setBusyUserId] = useState<string | null>(null);

  const users: User[] = data || [];
  const totalCount = users.length;
  const activeCount = users.filter((u) => u.is_active).length;
  const pendingCount = users.filter((u) => !u.is_active).length;

  async function handleToggleStatus(user: User) {
    setBusyUserId(user.id);
    setActionNotice(null);
    try {
      if (user.is_active) {
        await endpoints.deactivateUser(user.id);
        setActionNotice(`⛔ Operator access suspended for "${user.full_name}". They can no longer log in or perform actions.`);
      } else {
        await endpoints.activateUser(user.id);
        setActionNotice(`✅ Access approved and activated for "${user.full_name}".`);
      }
      await reload();
    } catch (err) {
      setActionNotice(err instanceof Error ? err.message : "Failed to update account status");
    } finally {
      setBusyUserId(null);
    }
  }

  async function handleRoleChange(user: User, newRole: Role) {
    if (user.role === newRole) return;
    setBusyUserId(user.id);
    setActionNotice(null);
    try {
      await endpoints.updateUserRole(user.id, newRole);
      setActionNotice(`🛡️ Role for "${user.full_name}" updated to "${humanize(newRole)}". Permissions adjusted.`);
      await reload();
    } catch (err) {
      setActionNotice(err instanceof Error ? err.message : "Failed to change operator role");
    } finally {
      setBusyUserId(null);
    }
  }

  async function handleDeleteUser(user: User) {
    if (!window.confirm(`Are you sure you want to permanently revoke and delete operator account "${user.full_name}" (${user.email})?`)) {
      return;
    }
    setBusyUserId(user.id);
    setActionNotice(null);
    try {
      await endpoints.deleteUser(user.id);
      setActionNotice(`🗑️ Account for "${user.full_name}" has been permanently purged from the platform.`);
      await reload();
    } catch (err) {
      setActionNotice(err instanceof Error ? err.message : "Failed to delete user account");
    } finally {
      setBusyUserId(null);
    }
  }

  return (
    <div className="space-y-6">
      {/* Misuse Prevention & Security Banner */}
      <div className="rounded-2xl border border-line/90 bg-gradient-to-r from-panel via-raised to-panel p-5 shadow-glass">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 mb-1.5">
              <span className="h-2 w-2 rounded-full bg-cyan animate-pulse" />
              <span className="font-mono text-[0.6875rem] font-bold tracking-widest text-cyan uppercase">
                INSTITUTIONAL ACCESS CONTROL & FRAUD DEFENSE
              </span>
            </div>
            <h1 className="text-xl font-extrabold text-white">
              Operator Management & Permission Governance
            </h1>
            <p className="text-xs text-muted max-w-2xl mt-1">
              Prevent unauthorized platform misuse. College administrators have complete authority to grant permissions,
              change operator roles, suspend access, and enforce least-privilege security.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-center rounded-xl border border-line/80 bg-panel/80 px-4 py-2">
              <div className="text-lg font-mono font-bold text-white">{totalCount}</div>
              <div className="text-[0.625rem] font-mono text-muted uppercase">Total Users</div>
            </div>
            <div className="text-center rounded-xl border border-ok/40 bg-ok/10 px-4 py-2">
              <div className="text-lg font-mono font-bold text-ok">{activeCount}</div>
              <div className="text-[0.625rem] font-mono text-ok uppercase">Active</div>
            </div>
            <div className="text-center rounded-xl border border-sev-critical/40 bg-sev-critical/10 px-4 py-2">
              <div className="text-lg font-mono font-bold text-sev-critical">{pendingCount}</div>
              <div className="text-[0.625rem] font-mono text-sev-critical uppercase">Suspended / Pending</div>
            </div>
          </div>
        </div>

        {/* Protection Features Grid */}
        <div className="mt-4 pt-4 border-t border-line/70 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="flex items-start gap-2">
            <span className="text-cyan text-sm">🔒</span>
            <div>
              <strong className="text-white block font-medium">Zero Unauthorized Actions:</strong>
              <span className="text-muted text-[0.6875rem]">
                Non-admin users cannot execute firewall bans, isolate hosts, or alter detection policies.
              </span>
            </div>
          </div>

          <div className="flex items-start gap-2">
            <span className="text-ok text-sm">🛡️</span>
            <div>
              <strong className="text-white block font-medium">1-Click Instant Revocation:</strong>
              <span className="text-muted text-[0.6875rem]">
                Suspended accounts are locked out immediately; session tokens cannot be refreshed.
              </span>
            </div>
          </div>

          <div className="flex items-start gap-2">
            <span className="text-accent text-sm">📝</span>
            <div>
              <strong className="text-white block font-medium">SHA-256 Audit Accountability:</strong>
              <span className="text-muted text-[0.6875rem]">
                Every single query and mutating operation is logged with the operator's ID in the tamper-proof ledger.
              </span>
            </div>
          </div>
        </div>
      </div>

      {actionNotice && (
        <div className="rounded-xl border border-cyan/40 bg-cyan/10 p-3.5 text-xs font-mono text-cyan flex items-center justify-between">
          <span>{actionNotice}</span>
          <button
            type="button"
            onClick={() => setActionNotice(null)}
            className="text-muted hover:text-white ml-2 text-sm"
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Users Table Panel */}
      <Panel
        title="Registered Operators & Access Permissions"
        action={
          <Button size="sm" variant="ghost" onClick={reload} disabled={loading} className="text-xs">
            🔄 Refresh List
          </Button>
        }
      >
        {loading && !data ? (
          <Loading label="Loading operators" />
        ) : error ? (
          <ErrorNote message={error} onRetry={reload} />
        ) : !data || data.length === 0 ? (
          <EmptyState title="No operators registered" />
        ) : (
          <Table headers={["Operator", "Email", "Assigned Role", "Permissions Level", "Status", "Last Seen", "Admin Actions"]}>
            {users.map((user) => {
              const isSuperAdmin = user.email.toLowerCase() === "admin@threatplatform.dev";
              const isBusy = busyUserId === user.id;

              return (
                <tr key={user.id} className="hover:bg-raised/40 transition-colors">
                  <td className="py-3 pr-4">
                    <div className="font-semibold text-white">{user.full_name}</div>
                    <div className="text-[0.6875rem] font-mono text-faint">ID: {user.id.slice(0, 12)}…</div>
                  </td>

                  <td className="data py-3 pr-4 text-muted font-mono text-xs">
                    {user.email}
                  </td>

                  <td className="py-3 pr-4">
                    <Can do={PERMISSIONS.USER_MANAGE} fallback={<span className="text-xs">{humanize(user.role)}</span>}>
                      {isSuperAdmin ? (
                        <span className="inline-block px-2 py-0.5 rounded-full bg-cyan/20 border border-cyan/40 text-cyan text-[0.6875rem] font-mono font-bold">
                          Super Administrator
                        </span>
                      ) : (
                        <select
                          value={user.role}
                          disabled={isBusy}
                          onChange={(e) => handleRoleChange(user, e.target.value as Role)}
                          className="rounded-lg border border-line bg-raised px-2.5 py-1 text-xs text-ink font-mono focus:border-cyan focus:outline-none cursor-pointer"
                        >
                          <option value="security_analyst">Security Analyst</option>
                          <option value="environment_user">Environment Viewer</option>
                          <option value="super_admin">Super Admin</option>
                        </select>
                      )}
                    </Can>
                  </td>

                  <td className="py-3 pr-4 text-xs font-mono">
                    {user.role === "super_admin" ? (
                      <span className="text-cyan font-semibold">Full Control (All Tiers)</span>
                    ) : user.role === "security_analyst" ? (
                      <span className="text-ok">Triage & Containment</span>
                    ) : (
                      <span className="text-muted">Read-Only (Viewer)</span>
                    )}
                  </td>

                  <td className="py-3 pr-4 text-xs">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[0.6875rem] font-mono font-semibold border ${
                        user.is_active
                          ? "bg-ok/10 border-ok/40 text-ok"
                          : "bg-sev-critical/10 border-sev-critical/40 text-sev-critical"
                      }`}
                    >
                      <span className={`h-1.5 w-1.5 rounded-full ${user.is_active ? "bg-ok" : "bg-sev-critical"}`} />
                      {user.is_active ? "Active" : "Suspended"}
                    </span>
                  </td>

                  <td className="py-3 text-xs text-muted">
                    {user.last_login_at ? formatDateTime(user.last_login_at) : "Never"}
                  </td>

                  <td className="py-3 text-xs">
                    {isSuperAdmin ? (
                      <span className="text-[0.6875rem] font-mono text-faint italic">System Root</span>
                    ) : (
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          disabled={isBusy}
                          onClick={() => handleToggleStatus(user)}
                          className={`text-xs px-2.5 py-1 ${
                            user.is_active
                              ? "text-sev-critical border-sev-critical/40 hover:bg-sev-critical/10"
                              : "text-ok border-ok/40 hover:bg-ok/10"
                          }`}
                        >
                          {isBusy ? "Updating…" : user.is_active ? "⛔ Suspend" : "✅ Activate"}
                        </Button>

                        <button
                          type="button"
                          disabled={isBusy}
                          onClick={() => handleDeleteUser(user)}
                          className="text-faint hover:text-sev-critical p-1 text-xs transition-colors cursor-pointer"
                          title="Permanently remove operator"
                        >
                          🗑️
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </Table>
        )}
      </Panel>
    </div>
  );
}
