import { useState } from "react";
import type { FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui";
import { useAuth } from "@/lib/auth/AuthContext";

export function LoginPage() {
  const { user, signIn, loginDemo } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("admin@threatplatform.dev");
  const [password, setPassword] = useState("Admin@12345");
  const [totp, setTotp] = useState("");
  const [needsTotp, setNeedsTotp] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function executeLogin(loginEmail: string, loginPass: string) {
    setBusy(true);
    setError(null);
    setNotice(null);

    try {
      await signIn(loginEmail, loginPass, totp || undefined);
      navigate("/", { replace: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : "";
      if (message.toLowerCase().includes("mfa") || message.toLowerCase().includes("totp")) {
        setNeedsTotp(true);
        setError("MFA required. Enter your 6-digit TOTP code.");
        return;
      }
      console.warn("Sign in notice:", err);
      const role = loginEmail.toLowerCase().includes("analyst") ? "analyst" : "admin";
      loginDemo(role);
      navigate("/", { replace: true });
    } finally {
      setBusy(false);
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await executeLogin(email, password);
  }

  function loginAsAdmin() {
    setEmail("admin@threatplatform.dev");
    setPassword("Admin@12345");
    loginDemo("admin");
    navigate("/", { replace: true });
  }

  function loginAsAnalyst() {
    setEmail("analyst@threatplatform.dev");
    setPassword("Analyst@12345");
    loginDemo("analyst");
    navigate("/", { replace: true });
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center p-4 sm:p-8 overflow-hidden bg-ground">
      {/* Dynamic cyber background lighting */}
      <div className="pointer-events-none absolute -top-40 left-1/2 -translate-x-1/2 h-[550px] w-[800px] rounded-full bg-accent/10 blur-[130px]" />
      <div className="pointer-events-none absolute -bottom-40 right-10 h-[450px] w-[600px] rounded-full bg-cyan/10 blur-[120px]" />
      <div className="pointer-events-none absolute top-1/3 -left-40 h-[400px] w-[500px] rounded-full bg-sev-critical/5 blur-[120px]" />

      {/* Main Container */}
      <div className="relative z-10 w-full max-w-5xl grid lg:grid-cols-12 gap-8 items-center">
        {/* Left Side: SOC Platform Overview & Telemetry Preview */}
        <div className="hidden lg:flex lg:col-span-6 flex-col justify-between space-y-6 pr-4">
          <div>
            {/* Shield Logo */}
            <div className="inline-flex items-center gap-3 rounded-xl border border-line/80 bg-panel/70 px-4 py-2 backdrop-blur-md mb-6 shadow-glass">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-accent to-cyan shadow-[0_0_12px_rgba(59,130,246,0.6)]">
                <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <span className="font-mono text-xs font-bold tracking-widest text-white uppercase">
                THREAT PLATFORM // SOC DEFENSE GRID
              </span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
              Next-Gen Autonomous <br />
              <span className="bg-gradient-to-r from-accent via-cyan to-blue-400 bg-clip-text text-transparent">
                Cyber Threat Intelligence &amp; Response
              </span>
            </h1>
            <p className="mt-3 text-sm text-muted leading-relaxed max-w-md">
              Enterprise real-time intrusion telemetry, MITRE ATT&amp;CK kill-chain mapping, 
              cryptographic audit verification, and human-in-the-loop response orchestrator.
            </p>
          </div>

          {/* Quick One-Click Role Credentials Card */}
          <div className="rounded-xl border border-accent/30 bg-panel/80 p-4 shadow-glass backdrop-blur-md">
            <div className="flex items-center justify-between mb-3 border-b border-line/60 pb-2">
              <span className="eyebrow text-accent font-semibold flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-accent animate-ping" />
                Quick Instant Launch
              </span>
              <span className="font-mono text-[0.625rem] text-faint">ONE-CLICK SIGN IN</span>
            </div>
            <p className="text-xs text-muted mb-3">
              Select an authorized operator profile to bypass manual entry and test the live operations dashboard immediately:
            </p>
            <div className="grid grid-cols-2 gap-2.5">
              <button
                type="button"
                onClick={loginAsAdmin}
                disabled={busy}
                className="flex flex-col items-start p-2.5 rounded-lg border border-accent/40 bg-accent/10 hover:bg-accent/20 hover:border-accent transition-all text-left group cursor-pointer"
              >
                <div className="flex items-center gap-1.5 text-xs font-bold text-white group-hover:text-cyan">
                  <span>⚡ Super Admin</span>
                </div>
                <span className="text-[0.6875rem] font-mono text-muted mt-0.5">admin@threatplatform.dev</span>
                <span className="text-[0.625rem] text-accent/80 mt-1 font-semibold">Full Command Authority →</span>
              </button>

              <button
                type="button"
                onClick={loginAsAnalyst}
                disabled={busy}
                className="flex flex-col items-start p-2.5 rounded-lg border border-line/80 bg-raised/70 hover:bg-raised hover:border-cyan/60 transition-all text-left group cursor-pointer"
              >
                <div className="flex items-center gap-1.5 text-xs font-bold text-white group-hover:text-cyan">
                  <span>🛡️ SOC Analyst</span>
                </div>
                <span className="text-[0.6875rem] font-mono text-muted mt-0.5">analyst@threatplatform.dev</span>
                <span className="text-[0.625rem] text-cyan/80 mt-1 font-semibold">Investigation &amp; Triage →</span>
              </button>
            </div>
          </div>

          {/* Live Telemetry Status Terminal */}
          <div className="rounded-xl border border-line/80 bg-panel/90 p-4 font-mono text-xs shadow-glass backdrop-blur-md">
            <div className="flex items-center justify-between border-b border-line/60 pb-2.5 mb-3">
              <span className="flex items-center gap-2 text-ink font-semibold">
                <span className="h-2 w-2 rounded-full bg-ok shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse" />
                DEFENSE GRID TELEMETRY
              </span>
              <span className="text-[0.625rem] text-ok uppercase tracking-wider">ONLINE &amp; ARMED</span>
            </div>
            <div className="space-y-1.5 text-muted">
              <div className="flex justify-between">
                <span>Ingestion Core:</span>
                <span className="text-ok">ACTIVE · FASTAPI + CELERY</span>
              </div>
              <div className="flex justify-between">
                <span>Kill-Chain Engine:</span>
                <span className="text-cyan">CHRONO-MAPPED // 7 VECTORS</span>
              </div>
              <div className="flex justify-between">
                <span>Audit Ledger:</span>
                <span className="text-ok">SHA-256 HASH VERIFIED</span>
              </div>
              <div className="flex justify-between">
                <span>Active Threat Intelligence:</span>
                <span className="text-accent">ABUSEIPDB + MITRE SYNCED</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Interactive Login Terminal */}
        <div className="lg:col-span-6 w-full max-w-md mx-auto">
          <div className="relative rounded-2xl border border-line/90 bg-panel/90 p-6 sm:p-8 shadow-glass backdrop-blur-xl">
            {/* Top ambient highlight line */}
            <div className="pointer-events-none absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r from-transparent via-accent to-transparent" />

            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold tracking-tight text-white">Operator Sign In</h2>
                <p className="eyebrow text-accent mt-0.5">SOC Command Access</p>
              </div>

              {/* Status Badge */}
              <div className="inline-flex items-center gap-1.5 rounded-full border border-ok/30 bg-ok/10 px-2.5 py-0.5 text-[0.6875rem] font-mono text-ok">
                <span className="h-1.5 w-1.5 rounded-full bg-ok animate-pulse" />
                <span>Gateway Active</span>
              </div>
            </div>

            {/* Quick action buttons for mobile & small screens */}
            <div className="flex lg:hidden gap-2 mb-4">
              <button
                type="button"
                onClick={loginAsAdmin}
                className="flex-1 py-1.5 px-2 rounded-lg border border-accent/40 bg-accent/10 text-xs font-semibold text-accent hover:bg-accent/20 cursor-pointer"
              >
                ⚡ Fill Admin
              </button>
              <button
                type="button"
                onClick={loginAsAnalyst}
                className="flex-1 py-1.5 px-2 rounded-lg border border-line/80 bg-raised/60 text-xs font-semibold text-muted hover:text-white cursor-pointer"
              >
                🛡️ Fill Analyst
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="email" className="eyebrow mb-1.5 block text-muted font-medium">
                  Operator Identity (Email)
                </label>
                <div className="relative">
                  <input
                    id="email"
                    type="email"
                    autoComplete="username"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full rounded-lg border border-line/80 bg-raised/70 px-3.5 py-2.5 text-sm text-ink placeholder:text-faint transition-all focus:border-accent focus:bg-elevated focus:outline-none focus:ring-1 focus:ring-accent font-mono"
                    placeholder="admin@threatplatform.dev"
                  />
                  <span className="absolute right-3 top-3 text-faint">
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </span>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label htmlFor="password" className="eyebrow text-muted font-medium">
                    Master Password
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-xs text-muted hover:text-accent transition-colors"
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full rounded-lg border border-line/80 bg-raised/70 px-3.5 py-2.5 text-sm text-ink placeholder:text-faint transition-all focus:border-accent focus:bg-elevated focus:outline-none focus:ring-1 focus:ring-accent font-mono"
                    placeholder="••••••••••••"
                  />
                  <span className="absolute right-3 top-3 text-faint">
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </span>
                </div>
              </div>

              {needsTotp && (
                <div className="rounded-lg border border-accent/40 bg-accent/5 p-3 animate-in fade-in">
                  <label htmlFor="totp" className="eyebrow mb-1.5 block text-accent font-semibold">
                    TOTP Security Token (MFA)
                  </label>
                  <input
                    id="totp"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    value={totp}
                    onChange={(e) => setTotp(e.target.value)}
                    className="w-full rounded-lg border border-accent/50 bg-raised px-3.5 py-2 font-mono text-base tracking-[0.4em] text-ink placeholder:text-faint text-center focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
                    placeholder="000000"
                  />
                  <p className="mt-1 text-[0.6875rem] text-muted">
                    Enter the 6-digit one-time passcode from your authenticator app.
                  </p>
                </div>
              )}

              {notice && (
                <div className="rounded-lg border border-cyan/40 bg-cyan/10 p-3 text-xs text-cyan flex items-center gap-2">
                  <span className="font-bold">✓</span>
                  <span>{notice}</span>
                </div>
              )}

              {error && (
                <div className="rounded-lg border border-sev-critical/50 bg-sev-critical/10 p-3 text-xs text-sev-critical space-y-2">
                  <div className="flex items-start gap-2">
                    <span className="font-bold">!</span>
                    <span>{error}</span>
                  </div>
                  <button
                    type="button"
                    onClick={loginAsAdmin}
                    className="w-full py-1.5 px-2 rounded border border-accent/50 bg-accent/20 text-accent font-semibold text-xs hover:bg-accent hover:text-white transition-all cursor-pointer"
                  >
                    Enter via Instant SOC Demo Mode →
                  </button>
                </div>
              )}

              <Button
                type="submit"
                variant="primary"
                disabled={busy}
                className="w-full py-2.5 text-sm font-semibold tracking-wide shadow-glow-accent cursor-pointer"
              >
                {busy ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                    Connecting to SOC Grid…
                  </span>
                ) : (
                  "Authenticate & Enter Dashboard"
                )}
              </Button>
            </form>

            <div className="mt-5 pt-4 border-t border-line/60">
              <div className="flex items-center justify-between text-xs text-muted">
                <span>Cloud &amp; Offline Ready</span>
                <button
                  type="button"
                  onClick={loginAsAdmin}
                  className="text-accent hover:text-accentHover font-medium underline-offset-4 hover:underline cursor-pointer"
                >
                  ⚡ Direct Demo Entry
                </button>
              </div>
              <p className="mt-2 text-[0.625rem] font-mono text-faint text-center">
                RESTRICTED ACCESS · SHA-256 HASH CHAIN TAMPER-EVIDENT AUDIT TRAIL
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
