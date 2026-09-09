import { useState } from "react";
import type { FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui";
import { useAuth } from "@/lib/auth/AuthContext";

export function LoginPage() {
  const { user, signIn } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [totp, setTotp] = useState("");
  const [needsTotp, setNeedsTotp] = useState(false);
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

  const field =
    "w-full rounded-md border border-line bg-raised px-3 py-2 text-sm text-ink placeholder:text-faint";

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <div className="mb-6">
          <h1 className="text-lg font-semibold tracking-tight">Threat Console</h1>
          <p className="eyebrow mt-1">Sign in to continue</p>
        </div>

        <form onSubmit={handleSubmit} className="panel space-y-4 p-5">
          <div>
            <label htmlFor="email" className="eyebrow mb-1.5 block">
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={field}
              placeholder="you@organisation.example"
            />
          </div>

          <div>
            <label htmlFor="password" className="eyebrow mb-1.5 block">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={field}
            />
          </div>

          {needsTotp && (
            <div>
              <label htmlFor="totp" className="eyebrow mb-1.5 block">
                Authenticator code
              </label>
              <input
                id="totp"
                inputMode="numeric"
                autoComplete="one-time-code"
                value={totp}
                onChange={(e) => setTotp(e.target.value)}
                className={`${field} data tracking-[0.3em]`}
                placeholder="000000"
              />
            </div>
          )}

          {error && (
            <p className="rounded-md border border-sev-critical/40 bg-sev-critical/10 px-3 py-2 text-xs text-sev-critical">
              {error}
            </p>
          )}

          <Button type="submit" variant="primary" disabled={busy} className="w-full">
            {busy ? "Signing in…" : "Sign in"}
          </Button>
        </form>

        <p className="mt-4 text-center text-xs text-faint">
          Access is logged. Every action you take is recorded in the audit trail.
        </p>
      </div>
    </div>
  );
}
