import { useState } from "react";
import type { FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui";
import { useAuth } from "@/lib/auth/AuthContext";

export function LoginPage() {
  const { user, signIn } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [totp, setTotp] = useState("");
  const [needsTotp, setNeedsTotp] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await signIn(email, password, totp || undefined);
      navigate("/", { replace: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Sign in failed";
      if (message.toLowerCase().includes("mfa")) setNeedsTotp(true);
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  function fillDemoCredentials() {
    setEmail("admin@threatplatform.dev");
    setPassword("Admin@12345");
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
        <div className="hidden lg:flex lg:col-span-6 flex-col justify-between space-y-8 pr-4">
          <div>
            {/* Shield Logo */}
            <div className="inline-flex items-center gap-3 rounded-xl border border-line/80 bg-panel/70 px-4 py-2 backdrop-blur-md mb-6 shadow-glass">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-accent to-cyan shadow-[0_0_12px_rgba(59,130,246,0.6)]">
                <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <span className="font-mono text-xs font-bold tracking-widest text-white uppercase">
                THREAT PLATFORM // V1.0
              </span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
              Next-Gen Autonomous <br />
              <span className="bg-gradient-to-r from-accent via-cyan to-blue-400 bg-clip-text text-transparent">
                Cyber Defense Grid
              </span>
            </h1>
            <p className="mt-3 text-sm text-muted leading-relaxed max-w-md">
              Enterprise real-time intrusion detection, MITRE ATT&amp;CK kill-chain mapping,
              and tamper-evident incident response.
            </p>
          </div>

          {/* Live Telemetry Status Terminal */}
          <div className="rounded-xl border border-line/80 bg-panel/90 p-4 font-mono text-xs shadow-glass backdrop-blur-md">
            <div className="flex items-center justify-between border-b border-line/60 pb-2.5 mb-3">
              <span className="flex items-center gap-2 text-ink font-semibold">
                <span className="h-2 w-2 rounded-full bg-ok shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse" />
                SYSTEM TELEMETRY FEED
              </span>
              <span className="text-[0.625rem] text-faint uppercase">TLS 1.3 // ENCRYPTED</span>
            </div>
            <div className="space-y-1.5 text-muted">
              <div className="flex justify-between">
                <span>Ingestion Pipeline:</span>
                <span className="text-ok">ACTIVE · 0 PENDING</span>
              </div>
              <div className="flex justify-between">
                <span>Correlation &amp; Kill-Chain:</span>
                <span className="text-cyan">CHRONO-MAPPED</span>
              </div>
              <div className="flex justify-between">
                <span>Audit Trail Ledger:</span>
                <span className="text-ok">SHA-256 HASH VERIFIED</span>
              </div>
              <div className="flex justify-between">
                <span>Active Threat Intelligence:</span>
                <span className="text-accent">ABUSEIPDB + MITRE SYNCED</span>
              </div>
            </div>
          </div>

          {/* Security Compliance Badges */}
          <div className="flex items-center gap-4 text-xs font-mono text-faint">
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-accent" />
              SOC 2 COMPLIANT
            </span>
            <span>•</span>
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan" />
              MITRE ATT&amp;CK
            </span>
            <span>•</span>
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-ok" />
              AIR-GAP READY
            </span>
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
                <p className="eyebrow text-accent mt-0.5">Secure Gateway Authentication</p>
              </div>

              {/* Quick Fill Button */}
              <button
                type="button"
                onClick={fillDemoCredentials}
                className="inline-flex items-center gap-1.5 rounded-lg border border-accent/40 bg-accent/10 px-2.5 py-1 text-[0.6875rem] font-mono font-medium text-accent hover:bg-accent/20 transition-all cursor-pointer shadow-sm"
                title="Populate default admin test credentials"
              >
                <span>⚡ Fill Admin</span>
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
                    className="w-full rounded-lg border border-line/80 bg-raised/70 px-3.5 py-2.5 text-sm text-ink placeholder:text-faint transition-all focus:border-accent focus:bg-elevated focus:outline-none focus:ring-1 focus:ring-accent"
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
                    className="w-full rounded-lg border border-line/80 bg-raised/70 px-3.5 py-2.5 text-sm text-ink placeholder:text-faint transition-all focus:border-accent focus:bg-elevated focus:outline-none focus:ring-1 focus:ring-accent"
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
                    Enter the 6-digit one-time passcode from your authenticator device.
                  </p>
                </div>
              )}

              {error && (
                <div className="rounded-lg border border-sev-critical/50 bg-sev-critical/10 p-3 text-xs text-sev-critical flex items-start gap-2">
                  <span className="font-bold">!</span>
                  <span>{error}</span>
                </div>
              )}

              <Button
                type="submit"
                variant="primary"
                disabled={busy}
                className="w-full py-2.5 text-sm font-semibold tracking-wide shadow-glow-accent cursor-pointer"
              >
                {busy ? (
                  <span className="flex items-center gap-2">
                    <span className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                    Authenticating…
                  </span>
                ) : (
                  "Authenticate & Connect"
                )}
              </Button>
            </form>

            <div className="mt-6 border-t border-line/60 pt-4 text-center">
              <p className="text-xs text-muted">
                New security operator?{" "}
                <Link to="/register" className="text-accent font-medium hover:text-accentHover underline-offset-4 hover:underline">
                  Register credential
                </Link>
              </p>
              <p className="mt-2 text-[0.625rem] font-mono text-faint">
                RESTRICTED SYSTEM · ALL MUTATING ACTIONS CRYPTOGRAPHICALLY RECORDED
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
