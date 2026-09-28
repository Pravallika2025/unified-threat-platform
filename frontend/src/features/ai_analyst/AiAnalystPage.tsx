import { useEffect, useRef, useState } from "react";

// ─────────────────────────────────────────────────────────────────────────────
// Gemini AI Threat Analyst — powered by Google Gemini Flash API (free tier)
// Uses VITE_GEMINI_API_KEY from .env.local
// ─────────────────────────────────────────────────────────────────────────────

const GEMINI_MODEL = "gemini-2.0-flash";
const GEMINI_ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

const SYSTEM_PROMPT = `You are an expert Cyber Threat Intelligence (CTI) Analyst working in a Security Operations Center (SOC). 
You assist security analysts with:
- Interpreting MITRE ATT&CK tactics, techniques, and procedures (TTPs)
- Analyzing threat indicators (IPs, hashes, domains, CVEs)
- Explaining attack kill-chain stages and lateral movement patterns
- Recommending containment, eradication and recovery actions
- Summarizing incident timelines and writing executive briefings
- Explaining anomaly detection results and risk scores
- Providing threat hunting queries (Sigma, YARA, KQL, Splunk SPL)

You are integrated into the Unified Multi-Environment Cyber Threat Detection & Response Platform — a real-time SOC dashboard. Always respond in a structured, professional manner suitable for a security analyst. Use bullet points, headings, and code blocks where appropriate.`;

interface Message {
  role: "user" | "model";
  text: string;
  ts: number;
}

const QUICK_PROMPTS = [
  "Explain MITRE T1059 - Command Scripting Interpreter",
  "What is lateral movement in a cyber attack?",
  "How do I investigate a brute-force login alert?",
  "Explain SHA-256 hash verification in audit logs",
  "What does a Risk Score of 85 mean?",
  "Write a Sigma rule for detecting PowerShell execution",
  "Summarize the MITRE ATT&CK kill chain",
  "How to contain a ransomware incident?",
];

export function AiAnalystPage() {
  const apiKey = import.meta.env.VITE_GEMINI_API_KEY as string | undefined;
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [localKey, setLocalKey] = useState<string>(() => localStorage.getItem("tp.gemini_key") || "");
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const effectiveKey = apiKey || localKey;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(text: string) {
    if (!text.trim() || loading) return;
    setError(null);

    const userMsg: Message = { role: "user", text: text.trim(), ts: Date.now() };
    const history = [...messages, userMsg];
    setMessages(history);
    setInput("");
    setLoading(true);

    // Build Gemini contents payload (multi-turn)
    // Simpler flat approach: just pass the full conversation
    const flatContents = history.map((m) => ({
      role: m.role,
      parts: [{ text: m.text }],
    }));

    // For single-turn simplicity with system context
    const payload = {
      system_instruction: {
        parts: [{ text: SYSTEM_PROMPT }],
      },
      contents: flatContents,
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 1024,
      },
    };

    try {
      const res = await fetch(`${GEMINI_ENDPOINT}?key=${effectiveKey}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.error?.message || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const reply = data?.candidates?.[0]?.content?.parts?.[0]?.text || "No response received.";
      setMessages([...history, { role: "model", text: reply, ts: Date.now() }]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setError(`Gemini API Error: ${msg}`);
      // Remove the user message we added if there was an error
      setMessages(history.slice(0, -1));
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  }

  function saveLocalKey() {
    if (apiKeyInput.trim()) {
      localStorage.setItem("tp.gemini_key", apiKeyInput.trim());
      setLocalKey(apiKeyInput.trim());
      setApiKeyInput("");
    }
  }

  function clearLocalKey() {
    localStorage.removeItem("tp.gemini_key");
    setLocalKey("");
  }

  function formatText(text: string) {
    // Basic markdown-like rendering
    const lines = text.split("\n");
    return lines.map((line, i) => {
      if (line.startsWith("### ")) return <h3 key={i} className="text-sm font-bold text-white mt-3 mb-1">{line.slice(4)}</h3>;
      if (line.startsWith("## ")) return <h2 key={i} className="text-sm font-extrabold text-cyan mt-4 mb-1">{line.slice(3)}</h2>;
      if (line.startsWith("# ")) return <h1 key={i} className="text-base font-extrabold text-accent mt-4 mb-2">{line.slice(2)}</h1>;
      if (line.startsWith("- ") || line.startsWith("* ")) return <li key={i} className="text-xs text-ink ml-4 list-disc">{line.slice(2)}</li>;
      if (line.startsWith("```")) return <div key={i} className="font-mono text-[0.7rem] text-ok" />;
      if (line.trim() === "") return <div key={i} className="h-1.5" />;
      return <p key={i} className="text-xs text-ink leading-relaxed">{line}</p>;
    });
  }

  return (
    <div className="flex flex-col h-full min-h-0 overflow-hidden">
      {/* Header */}
      <div className="px-6 pt-5 pb-4 border-b border-line/60 flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-accent to-cyan flex items-center justify-center shadow-[0_0_10px_rgba(59,130,246,0.5)]">
              <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17H3a2 2 0 01-2-2V5a2 2 0 012-2h16a2 2 0 012 2v10a2 2 0 01-2 2h-2m-6-8a2 2 0 110-4 2 2 0 010 4z" />
              </svg>
            </div>
            <h1 className="text-lg font-extrabold text-white tracking-tight">Gemini AI Threat Analyst</h1>
            <span className="px-2 py-0.5 rounded-full bg-accent/20 border border-accent/40 text-accent text-[0.65rem] font-mono font-bold">
              GOOGLE GEMINI FLASH
            </span>
          </div>
          <p className="text-xs text-muted">
            Ask about threats, MITRE ATT&amp;CK, incidents, IOCs, containment strategies, and more.
          </p>
        </div>

        {/* API Key Status */}
        <div className="text-right">
          {effectiveKey ? (
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 text-ok text-[0.6875rem] font-mono">
                <span className="h-1.5 w-1.5 rounded-full bg-ok animate-pulse" />
                LLM Connected
              </span>
              {!apiKey && (
                <button onClick={clearLocalKey} className="text-[0.6rem] text-faint hover:text-sev-critical cursor-pointer">
                  ✕ Remove
                </button>
              )}
            </div>
          ) : (
            <span className="text-[0.6875rem] text-sev-critical font-mono">⚠ API Key Required</span>
          )}
        </div>
      </div>

      {/* API Key Setup (if not configured) */}
      {!effectiveKey && (
        <div className="mx-6 mt-4 p-4 rounded-xl border border-accent/40 bg-accent/5 space-y-3">
          <div className="flex items-center gap-2">
            <svg className="h-4 w-4 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
            <span className="text-sm font-bold text-white">Connect Google Gemini API</span>
          </div>
          <p className="text-xs text-muted">
            Get a <strong className="text-accent">free API key</strong> from{" "}
            <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" className="text-cyan hover:underline">
              aistudio.google.com/apikey
            </a>{" "}
            — no credit card required. The key is stored only in your browser.
          </p>
          <div className="flex gap-2">
            <input
              type="password"
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
              placeholder="AIza..."
              className="flex-1 rounded-lg border border-line/80 bg-raised/70 px-3 py-2 text-sm text-ink font-mono placeholder:text-faint focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
              onKeyDown={(e) => e.key === "Enter" && saveLocalKey()}
            />
            <button
              onClick={saveLocalKey}
              className="px-4 py-2 rounded-lg bg-accent text-white text-sm font-semibold hover:bg-accentHover transition-all cursor-pointer"
            >
              Connect
            </button>
          </div>
          <p className="text-[0.625rem] text-faint">
            Or set <code className="font-mono text-accent">VITE_GEMINI_API_KEY=AIza...</code> in{" "}
            <code className="font-mono">.env.local</code> for permanent configuration.
          </p>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 min-h-0">
        {messages.length === 0 && (
          <div className="space-y-4">
            <div className="text-center py-6">
              <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-accent/20 to-cyan/20 border border-accent/30 mb-3">
                <svg className="h-7 w-7 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-white mb-1">Gemini AI Threat Analyst Ready</p>
              <p className="text-xs text-muted max-w-sm mx-auto">
                Ask any cybersecurity question — threat analysis, MITRE ATT&amp;CK, IOC investigation, incident response, or Sigma rules.
              </p>
            </div>

            {/* Quick Prompts */}
            <div>
              <p className="text-[0.6875rem] text-faint uppercase tracking-wider font-semibold mb-2">Quick Prompts</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {QUICK_PROMPTS.map((p, i) => (
                  <button
                    key={i}
                    onClick={() => effectiveKey && sendMessage(p)}
                    disabled={!effectiveKey}
                    className="text-left px-3 py-2 rounded-lg border border-line/80 bg-raised/50 hover:bg-panel hover:border-accent/50 text-xs text-muted hover:text-ink transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
            {/* Avatar */}
            <div className={`flex-shrink-0 h-7 w-7 rounded-full flex items-center justify-center text-[0.65rem] font-bold ${
              m.role === "user"
                ? "bg-accent text-white"
                : "bg-gradient-to-br from-accent to-cyan text-white"
            }`}>
              {m.role === "user" ? "U" : "AI"}
            </div>

            {/* Bubble */}
            <div className={`max-w-[85%] rounded-xl px-4 py-3 space-y-0.5 ${
              m.role === "user"
                ? "bg-accent/20 border border-accent/30 text-ink"
                : "bg-panel border border-line/60 text-ink"
            }`}>
              {m.role === "model" ? (
                <div className="space-y-0.5">{formatText(m.text)}</div>
              ) : (
                <p className="text-xs text-ink">{m.text}</p>
              )}
              <p className="text-[0.6rem] text-faint pt-1">
                {new Date(m.ts).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex gap-3">
            <div className="flex-shrink-0 h-7 w-7 rounded-full bg-gradient-to-br from-accent to-cyan flex items-center justify-center text-[0.65rem] font-bold text-white">
              AI
            </div>
            <div className="bg-panel border border-line/60 rounded-xl px-4 py-3 flex items-center gap-2">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="h-1.5 w-1.5 rounded-full bg-accent animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </div>
              <span className="text-xs text-muted">Analyzing threat intelligence…</span>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="rounded-lg border border-sev-critical/50 bg-sev-critical/10 px-4 py-3 text-xs text-sev-critical flex items-start gap-2">
            <span className="font-bold">!</span>
            <span>{error}</span>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <div className="px-6 pb-5 pt-3 border-t border-line/60">
        <div className="relative flex gap-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!effectiveKey || loading}
            rows={2}
            placeholder={effectiveKey ? "Ask about threats, MITRE ATT&CK, incidents… (Enter to send, Shift+Enter for newline)" : "Connect Gemini API key to start chatting…"}
            className="flex-1 resize-none rounded-xl border border-line/80 bg-raised/70 px-4 py-3 text-sm text-ink placeholder:text-faint transition-all focus:border-accent focus:bg-elevated focus:outline-none focus:ring-1 focus:ring-accent disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!effectiveKey || loading || !input.trim()}
            className="self-end px-4 py-3 rounded-xl bg-accent text-white font-semibold text-sm hover:bg-accentHover transition-all shadow-glow-accent cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <span className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
            ) : (
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
        <div className="flex items-center justify-between mt-2">
          <p className="text-[0.625rem] font-mono text-faint">
            Powered by Google Gemini Flash · Free API · No data stored server-side
          </p>
          {messages.length > 0 && (
            <button
              onClick={() => { setMessages([]); setError(null); }}
              className="text-[0.6rem] text-faint hover:text-muted cursor-pointer"
            >
              Clear chat
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
