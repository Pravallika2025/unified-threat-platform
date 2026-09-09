import { useRef, useState } from "react";

import { Button, Panel } from "@/components/ui";
import { endpoints } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/useApi";

interface UploadResult {
  accepted: number;
  rejected: number;
  alerts_raised: number;
}

export function UploadPage() {
  const { data: environments, loading: envLoading } = useApi(() => endpoints.environments(), []);

  const [environmentId, setEnvironmentId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const field =
    "w-full rounded-md border border-line bg-raised px-3 py-2 text-sm text-ink focus:outline-none focus:border-accent/60";

  async function handleUpload() {
    if (!file) {
      setError("Please select a file.");
      return;
    }
    if (!environmentId) {
      setError("Please select an environment.");
      return;
    }
    setError(null);
    setResult(null);
    setBusy(true);
    try {
      const res = await endpoints.uploadLogFile(environmentId, file);
      setResult(res);
      setFile(null);
      if (fileRef.current) fileRef.current.value = "";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <div>
        <h1 className="text-lg font-semibold tracking-tight text-ink">Upload Log File</h1>
        <p className="mt-1 text-sm text-muted">
          Upload a log file to ingest, normalize, and run threat detection on it immediately.
        </p>
      </div>

      <Panel title="Select environment &amp; file">
        <div className="space-y-4">
          {/* Environment picker */}
          <div>
            <label htmlFor="upload-env" className="eyebrow mb-1.5 block">
              Environment
            </label>
            {envLoading ? (
              <p className="text-xs text-muted">Loading environments…</p>
            ) : (
              <select
                id="upload-env"
                value={environmentId}
                onChange={(e) => setEnvironmentId(e.target.value)}
                className={field}
              >
                <option value="">— choose an environment —</option>
                {(environments ?? []).map((env) => (
                  <option key={env.id} value={env.id}>
                    {env.name} ({env.type})
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* File picker */}
          <div>
            <label htmlFor="upload-file" className="eyebrow mb-1.5 block">
              Log file
            </label>
            <div className="relative">
              <input
                id="upload-file"
                ref={fileRef}
                type="file"
                accept=".log,.txt,.json,.csv,.cef,.leef"
                className="block w-full cursor-pointer rounded-md border border-line bg-raised text-sm text-muted
                  file:mr-3 file:cursor-pointer file:rounded-l-md file:border-0
                  file:bg-accent/15 file:px-3 file:py-2 file:text-xs file:font-medium file:text-accent
                  hover:file:bg-accent/25"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
            </div>
            {file && (
              <p className="mt-1.5 text-xs text-muted">
                Selected: <span className="text-ink">{file.name}</span>{" "}
                ({(file.size / 1024).toFixed(1)} KB)
              </p>
            )}
            <p className="mt-1.5 text-xs text-faint">
              Accepted: .log, .txt, .json, .csv, .cef, .leef
            </p>
          </div>

          {/* Error */}
          {error && (
            <p className="rounded-md border border-sev-critical/40 bg-sev-critical/10 px-3 py-2 text-xs text-sev-critical">
              {error}
            </p>
          )}

          {/* Success result */}
          {result && (
            <div className="rounded-md border border-ok/40 bg-ok/10 px-4 py-3 text-sm">
              <p className="font-medium text-ok">✓ Upload processed successfully</p>
              <dl className="mt-2 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-md border border-line bg-raised p-2">
                  <dt className="eyebrow">Accepted</dt>
                  <dd className="data mt-1 text-lg font-semibold text-ink">{result.accepted}</dd>
                </div>
                <div className="rounded-md border border-line bg-raised p-2">
                  <dt className="eyebrow">Rejected</dt>
                  <dd className="data mt-1 text-lg font-semibold text-muted">{result.rejected}</dd>
                </div>
                <div className="rounded-md border border-accent/30 bg-accent/10 p-2">
                  <dt className="eyebrow text-accent">Alerts</dt>
                  <dd className="data mt-1 text-lg font-semibold text-accent">{result.alerts_raised}</dd>
                </div>
              </dl>
            </div>
          )}

          <Button
            variant="primary"
            disabled={busy || !file || !environmentId}
            className="w-full"
            onClick={handleUpload}
          >
            {busy ? (
              <span className="flex items-center gap-2">
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                Uploading…
              </span>
            ) : (
              "Upload &amp; Analyse"
            )}
          </Button>
        </div>
      </Panel>

      <p className="text-xs text-faint">
        Uploaded files go through the full ingestion pipeline: parse → normalize → detect → risk-score.
        Alerts raised will appear in the dashboard immediately.
      </p>
    </div>
  );
}
