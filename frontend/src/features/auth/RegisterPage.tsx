import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui";
import { endpoints } from "@/lib/api/endpoints";

export function RegisterPage() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [success, setSuccess] = useState(false);

  const field =
    "w-full rounded-md border border-line bg-raised px-3 py-2 text-sm text-ink placeholder:text-faint focus:outline-none focus:border-accent/60";

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setBusy(true);
    try {
      await endpoints.register(email, fullName, password);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    } finally {
      setBusy(false);
    }
  }

  if (success) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6">
        <div className="w-full max-w-sm text-center">
          <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-full border border-ok/40 bg-ok/10">
            <svg className="h-7 w-7 text-ok" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-ink">Account created!</h2>
          <p className="mt-2 text-sm text-muted">
            Your account has been created as a <span className="text-accent">Security Analyst</span>.
            An admin may need to assign you to an environment.
          </p>
          <Button
            variant="primary"
            className="mt-6 w-full"
            onClick={() => navigate("/login", { replace: true })}
          >
            Go to sign in
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <div className="mb-6">
          <h1 className="text-lg font-semibold tracking-tight">Threat Console</h1>
          <p className="eyebrow mt-1">Create a new account</p>
        </div>

        <form onSubmit={handleSubmit} className="panel space-y-4 p-5">
          <div>
            <label htmlFor="fullName" className="eyebrow mb-1.5 block">
              Full name
            </label>
            <input
              id="fullName"
              type="text"
              required
              autoComplete="name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className={field}
              placeholder="Jane Smith"
            />
          </div>

          <div>
            <label htmlFor="reg-email" className="eyebrow mb-1.5 block">
              Email
            </label>
            <input
              id="reg-email"
              type="email"
              required
              autoComplete="username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={field}
              placeholder="you@organisation.example"
            />
          </div>

          <div>
            <label htmlFor="reg-password" className="eyebrow mb-1.5 block">
              Password
            </label>
            <input
              id="reg-password"
              type="password"
              required
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={field}
              placeholder="Min 8 characters"
            />
          </div>

          <div>
            <label htmlFor="confirm-password" className="eyebrow mb-1.5 block">
              Confirm password
            </label>
            <input
              id="confirm-password"
              type="password"
              required
              autoComplete="new-password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              className={field}
            />
          </div>

          {error && (
            <p className="rounded-md border border-sev-critical/40 bg-sev-critical/10 px-3 py-2 text-xs text-sev-critical">
              {error}
            </p>
          )}

          <Button type="submit" variant="primary" disabled={busy} className="w-full">
            {busy ? "Creating account…" : "Create account"}
          </Button>
        </form>

        <p className="mt-4 text-center text-xs text-muted">
          Already have an account?{" "}
          <Link to="/login" className="text-accent hover:underline">
            Sign in
          </Link>
        </p>

        <p className="mt-2 text-center text-xs text-faint">
          Access is logged. Every action you take is recorded in the audit trail.
        </p>
      </div>
    </div>
  );
}
