import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "@/lib/auth/AuthContext";
import { useLiveFeed } from "@/lib/realtime/socket";
import { formatTime } from "@/lib/utils/format";

const NAV = [
  { to: "/", label: "Overview", end: true },
  { to: "/live", label: "Live monitor" },
  { to: "/incidents", label: "Incidents" },
  { to: "/alerts", label: "Alerts" },
  { to: "/review", label: "Review queue" },
  { to: "/environments", label: "Environments" },
  { to: "/users", label: "Users" },
  { to: "/audit", label: "Audit log" },
];

export function Shell() {
  const { user, signOut } = useAuth();
  const { connected, lastMessageAt } = useLiveFeed();

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-56 shrink-0 border-r border-line bg-panel md:block">
        <div className="border-b border-line px-4 py-4">
          <p className="text-sm font-semibold tracking-tight">Threat Console</p>
          <p className="eyebrow mt-0.5">Detection &amp; response</p>
        </div>

        <nav className="p-2">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `block rounded-md px-3 py-2 text-sm transition-colors ${
                  isActive ? "bg-accent/15 text-accent" : "text-muted hover:bg-raised hover:text-ink"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between gap-4 border-b border-line bg-panel px-4 py-3">
          <div className="flex items-center gap-2 text-xs">
            <span
              className={`h-2 w-2 rounded-full ${connected ? "bg-ok" : "bg-sev-medium"}`}
              aria-hidden
            />
            <span className="text-muted">
              {connected ? "Live" : "Reconnecting"}
              {lastMessageAt && ` · last event ${formatTime(lastMessageAt.toISOString())}`}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-xs text-ink">{user?.full_name}</p>
              <p className="eyebrow">{user?.role.replace(/_/g, " ")}</p>
            </div>
            <button
              onClick={signOut}
              className="rounded-md border border-line px-2.5 py-1 text-xs text-muted hover:border-muted hover:text-ink"
            >
              Sign out
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-x-hidden p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
