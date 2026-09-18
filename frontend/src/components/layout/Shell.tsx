import { ReactNode } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "@/lib/auth/AuthContext";
import { useLiveFeed } from "@/lib/realtime/socket";
import { formatTime } from "@/lib/utils/format";

interface NavItem {
  to: string;
  label: string;
  end?: boolean;
  icon: (active: boolean) => ReactNode;
}

const NAV_ITEMS: NavItem[] = [
  {
    to: "/",
    label: "Overview",
    end: true,
    icon: (active) => (
      <svg className={`h-4 w-4 shrink-0 ${active ? "text-accent" : "text-muted"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
    ),
  },
  {
    to: "/live",
    label: "Live monitor",
    icon: (active) => (
      <svg className={`h-4 w-4 shrink-0 ${active ? "text-accent" : "text-muted"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  },
  {
    to: "/incidents",
    label: "Incidents",
    icon: (active) => (
      <svg className={`h-4 w-4 shrink-0 ${active ? "text-accent" : "text-muted"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
  },
  {
    to: "/alerts",
    label: "Alerts",
    icon: (active) => (
      <svg className={`h-4 w-4 shrink-0 ${active ? "text-accent" : "text-muted"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
    ),
  },
  {
    to: "/threat-intel",
    label: "Threat intel",
    icon: (active) => (
      <svg className={`h-4 w-4 shrink-0 ${active ? "text-accent" : "text-muted"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
      </svg>
    ),
  },
  {
    to: "/review",
    label: "Review queue",
    icon: (active) => (
      <svg className={`h-4 w-4 shrink-0 ${active ? "text-accent" : "text-muted"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
      </svg>
    ),
  },
  {
    to: "/environments",
    label: "Environments",
    icon: (active) => (
      <svg className={`h-4 w-4 shrink-0 ${active ? "text-accent" : "text-muted"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    ),
  },
  {
    to: "/upload",
    label: "Upload logs",
    icon: (active) => (
      <svg className={`h-4 w-4 shrink-0 ${active ? "text-accent" : "text-muted"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
    ),
  },
  {
    to: "/reports",
    label: "Reports",
    icon: (active) => (
      <svg className={`h-4 w-4 shrink-0 ${active ? "text-accent" : "text-muted"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
  {
    to: "/users",
    label: "Users",
    icon: (active) => (
      <svg className={`h-4 w-4 shrink-0 ${active ? "text-accent" : "text-muted"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
  },
  {
    to: "/audit",
    label: "Audit log",
    icon: (active) => (
      <svg className={`h-4 w-4 shrink-0 ${active ? "text-accent" : "text-muted"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
  },
];

import { isMockMode } from "@/lib/api/endpoints";

export function Shell() {
  const { user, signOut } = useAuth();
  const { connected, lastMessageAt } = useLiveFeed();

  return (
    <div className="flex min-h-screen bg-ground text-ink">
      {/* Sidebar */}
      <aside className="hidden w-64 shrink-0 border-r border-line/70 bg-panel/90 backdrop-blur-xl md:flex md:flex-col">
        {/* Brand Header */}
        <div className="flex items-center gap-3 border-b border-line/60 px-5 py-4">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-accent via-cyan to-blue-600 shadow-[0_0_15px_rgba(59,130,246,0.5)]">
            <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5">
              THREAT PLATFORM
            </p>
            <p className="font-mono text-[0.625rem] font-medium tracking-widest text-cyan uppercase">
              SOC DEFENSE // V1.0
            </p>
          </div>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 space-y-1 p-3 overflow-y-auto">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? "bg-accent/15 text-white font-semibold shadow-[0_0_12px_rgba(59,130,246,0.15)] before:absolute before:left-0 before:top-1.5 before:bottom-1.5 before:w-1 before:rounded-r before:bg-accent before:shadow-[0_0_8px_rgba(59,130,246,0.8)]"
                    : "text-muted hover:bg-raised/80 hover:text-ink hover:translate-x-0.5"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {item.icon(isActive)}
                  <span className="truncate">{item.label}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Telemetry Status Footer */}
        <div className="border-t border-line/60 p-3">
          <div className="rounded-lg border border-line/50 bg-surface/60 p-3">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 ${connected || isMockMode() ? "animate-ping bg-ok" : "animate-ping bg-sev-medium"}`} />
                <span className={`relative inline-flex h-2 w-2 rounded-full ${connected || isMockMode() ? "bg-ok shadow-[0_0_8px_rgba(16,185,129,0.8)]" : "bg-sev-medium"}`} />
              </span>
              <span className="font-mono text-[0.6875rem] font-semibold tracking-wide text-ink">
                {connected || isMockMode() ? "TELEMETRY LIVE" : "CONNECTING"}
              </span>
            </div>
            {lastMessageAt && (
              <p className="mt-1 font-mono text-[0.625rem] text-faint">
                Event: {formatTime(lastMessageAt.toISOString())}
              </p>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top App Header */}
        <header className="sticky top-0 z-20 flex items-center justify-between border-b border-line/70 bg-panel/80 px-6 py-3 backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-accent/30 bg-accent/10 px-2.5 py-0.5 font-mono text-[0.6875rem] font-medium text-accent">
              <span className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
              SOC OPERATIONS
            </span>
            {isMockMode() ? (
              <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-cyan/40 bg-cyan/10 px-2.5 py-0.5 font-mono text-[0.6875rem] font-semibold text-cyan">
                <span className="h-1.5 w-1.5 rounded-full bg-cyan animate-pulse" />
                SOC SANDBOX (STANDALONE DEMO)
              </span>
            ) : (
              <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-ok/40 bg-ok/10 px-2.5 py-0.5 font-mono text-[0.6875rem] font-semibold text-ok">
                <span className="h-1.5 w-1.5 rounded-full bg-ok animate-pulse" />
                BACKEND API (PORT 8000 CONNECTED)
              </span>
            )}
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 border-r border-line/60 pr-4">
              <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-accent/30 to-cyan/20 border border-accent/40 flex items-center justify-center font-mono text-xs font-bold text-accent">
                {user?.full_name?.charAt(0) ?? "U"}
              </div>
              <div className="text-right">
                <p className="text-xs font-semibold text-ink leading-tight">{user?.full_name}</p>
                <p className="eyebrow text-accent font-mono text-[0.625rem]">{user?.role?.replace(/_/g, " ")}</p>
              </div>
            </div>

            <button
              onClick={signOut}
              className="rounded-lg border border-line/80 bg-raised/50 px-3 py-1.5 text-xs font-medium text-muted transition-all hover:border-lineHover hover:bg-elevated hover:text-ink cursor-pointer"
            >
              Sign out
            </button>
          </div>
        </header>

        {/* Page View Container */}
        <main className="flex-1 overflow-x-hidden p-5 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
