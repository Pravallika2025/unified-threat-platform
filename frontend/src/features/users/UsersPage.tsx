import { EmptyState, ErrorNote, Loading, Panel, Table } from "@/components/ui";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";
import { formatDateTime, humanize } from "@/lib/utils/format";

export function UsersPage() {
  const { data, error, loading, reload } = useApi(() => endpoints.users(), []);

  return (
    <Panel title="Users and roles">
      {loading && !data ? (
        <Loading label="Loading users" />
      ) : error ? (
        <ErrorNote message={error} onRetry={reload} />
      ) : !data || data.length === 0 ? (
        <EmptyState title="No users" />
      ) : (
        <Table headers={["Name", "Email", "Role", "MFA", "Status", "Last signed in"]}>
          {data.map((user) => (
            <tr key={user.id}>
              <td className="py-2.5 pr-4">{user.full_name}</td>
              <td className="data py-2.5 pr-4 text-muted">{user.email}</td>
              <td className="py-2.5 pr-4 text-xs">{humanize(user.role)}</td>
              <td className="py-2.5 pr-4 text-xs">
                <span className={user.mfa_enabled ? "text-ok" : "text-sev-medium"}>
                  {user.mfa_enabled ? "On" : "Off"}
                </span>
              </td>
              <td className="py-2.5 pr-4 text-xs">
                <span className={user.is_active ? "text-ok" : "text-muted"}>
                  {user.is_active ? "Active" : "Disabled"}
                </span>
              </td>
              <td className="py-2.5 text-xs text-muted">
                {user.last_login_at ? formatDateTime(user.last_login_at) : "Never"}
              </td>
            </tr>
          ))}
        </Table>
      )}
    </Panel>
  );
}
