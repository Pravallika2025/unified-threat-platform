import { useEffect, useRef, useState } from "react";
import {
  askThreatAnalyst,
  cleanApiKey,
  clearStoredApiKey,
  getStoredApiKey,
  setStoredApiKey,
  testGeminiApiKey,
  type ChatMessage,
} from "@/lib/ai/threatAnalyst";

const QUICK_PROMPTS = [
  "Explain MITRE T1059 - Command Scripting Interpreter",
  "How to contain a ransomware incident (T1486)?",
  "What is lateral movement in a cyber attack?",
  "How do I investigate a brute-force login alert?",
  "Explain SHA-256 hash verification in audit logs",
  "What does a Risk Score of 85 mean?",
  "Write a Sigma rule for detecting PowerShell execution",
  "Summarize the MITRE ATT&CK kill chain",
];

export function AiAnalystPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [effectiveKey, setEffectiveKey] = useState<string>(() => getStoredApiKey());
  const [keyModal, setKeyModal] = useState(false);
  const [keyInput, setKeyInput] = useState("");
  const [keyTestStatus, setKeyTestStatus] = useState<{ testing: boolean; message: string | null; success?: boolean }>({
    testing: false,
    message: null,
  });

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(text: string) {
    const q = text.trim();
    if (!q || loading) return;
    setError(null);
    setNotice(null);

    const userMsg: ChatMessage = { role: "user", text: q, ts: Date.now() };
    const history = [...messages, userMsg];
    setMessages(history);
    setInput("");
    setLoading(true);

    try {
      const resp = await askThreatAnalyst(q, effectiveKey, history);
      setMessages([...history, { role: "model", text: resp.text, ts: Date.now() }]);
      if (resp.notice) {
        setNotice(resp.notice);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error analyzing query";
      setError(`Analyst Engine Error: ${msg}`);
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

  async function handleTestKey() {
    if (!keyInput.trim()) {
      setKeyTestStatus({ testing: false, message: "Please enter an API key to test.", success: false });
      return;
    }
    setKeyTestStatus({ testing: true, message: "Pinging Google Gemini API...", success: undefined });
    const res = await testGeminiApiKey(keyInput);
    setKeyTestStatus({ testing: false, message: res.message, success: res.valid });
  }

  function handleSaveKey() {
    const cleaned = cleanApiKey(keyInput);
    if (cleaned) {
      setStoredApiKey(cleaned);
      setEffectiveKey(cleaned);
      setKeyInput("");
      setKeyTestStatus({ testing: false, message: null });
      setKeyModal(false);
    } else {
      setKeyTestStatus({
        testing: false,
        message: "Key is invalid or contains placeholder text. Please enter a valid Google AI Studio key.",
        success: false,
      });
    }
  }

  function handleClearKey() {
    clearStoredApiKey();
    setEffectiveKey("");
    setKeyInput("");
    setKeyTestStatus({
      testing: false,
      message: "API key removed. Built-in SOC Threat Intelligence engine is now active.",
      success: true,
    });
    setTimeout(() => setKeyModal(false), 900);
  }

  function formatText(text: string) {
    const lines = text.split("\n");
    return lines.map((line, i) => {
      if (line.startsWith("### "))
        return (
          <h3 key={i} className="text-sm font-bold text-white mt-3 mb-1 flex items-center gap-1.5">
            {line.slice(4)}
          </h3>
        );
      if (line.startsWith("## "))
        return (
          <h2 key={i} className="text-sm font-extrabold text-cyan mt-4 mb-1">
            {line.slice(3)}
          </h2>
        );
      if (line.startsWith("# "))
        return (
          <h1 key={i} className="text-base font-extrabold text-accent mt-4 mb-2">
            {line.slice(2)}
          </h1>
        );
      if (line.startsWith("#### "))
        return (
          <h4 key={i} className="text-xs font-bold text-ink mt-2 mb-0.5">
            {line.slice(5)}
          </h4>
        );
      if (line.startsWith("- ") || line.startsWith("* "))
        return (
          <li key={i} className="text-xs text-ink/90 ml-4 list-disc leading-relaxed">
            {line.slice(2)}
          </li>
        );
      if (line.startsWith("```"))
        return <div key={i} className="font-mono text-[0.7rem] text-ok my-1" />;
      if (line.trim() === "") return <div key={i} className="h-1.5" />;
      return (
        <p key={i} className="text-xs text-ink/90 leading-relaxed font-sans">
          {line}
        </p>
      );
    });
  }

  return (
    <div className="flex flex-col h-full min-h-0 overflow-hidden">
      {/* Header */}
      <div className="px-6 pt-5 pb-4 border-b border-line/60 flex items-start justify-between bg-panel/50 backdrop-blur-md">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-accent to-cyan flex items-center justify-center shadow-[0_0_10px_rgba(59,130,246,0.5)]">
              <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17H3a2 2 0 01-2-2V5a2 2 0 012-2h16a2 2 0 012 2v10a2 2 0 01-2 2h-2m-6-8a2 2 0 110-4 2 2 0 010 4z"
                />
              </svg>
            </div>
            <h1 className="text-lg font-extrabold text-white tracking-tight">AI Threat Intelligence Analyst</h1>
            <span
              className={`px-2 py-0.5 rounded-full border text-[0.65rem] font-mono font-bold ${
                effectiveKey
                  ? "bg-accent/20 border-accent/40 text-accent"
                  : "bg-cyan/15 border-cyan/40 text-cyan"
              }`}
            >
              {effectiveKey ? "GOOGLE GEMINI 2.0 FLASH" : "BUILT-IN SOC REASONING"}
            </span>
          </div>
          <p className="text-xs text-muted">
            Interactive CTI copilot for MITRE ATT&amp;CK mapping, incident containment, IOC queries, and forensic playbooks.
          </p>
        </div>

        {/* Status & Key Config */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="inline-flex items-center gap-1.5 text-ok text-[0.6875rem] font-mono">
              <span className="h-2 w-2 rounded-full bg-ok shadow-[0_0_6px_rgba(34,197,94,0.8)] animate-pulse" />
              {effectiveKey ? "Live Gemini Active" : "SOC Engine Ready"}
            </span>
          </div>
          <button
            onClick={() => {
              setKeyInput(effectiveKey);
              setKeyTestStatus({ testing: false, message: null });
              setKeyModal(true);
            }}
            className="px-2.5 py-1 rounded-lg border border-cyan/40 bg-cyan/15 hover:bg-cyan hover:text-black text-cyan text-xs font-mono font-semibold transition-all cursor-pointer"
          >
            {effectiveKey ? "🔑 Key Configured" : "⚙ Connect Gemini API"}
          </button>
        </div>
      </div>

      {/* Notice Banner (if live key has issue and fell back) */}
      {notice && (
        <div className="mx-6 mt-3 px-3 py-2 rounded-lg bg-amber-950/40 border border-amber-800/50 text-amber-300 text-xs font-mono flex items-center justify-between">
          <span>{notice}</span>
          <button onClick={() => setNotice(null)} className="text-amber-400 hover:text-white ml-2 text-xs">
            ✕
          </button>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 min-h-0 scrollbar-thin">
        {messages.length === 0 && (
          <div className="space-y-4">
            <div className="text-center py-6">
              <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-accent/20 to-cyan/20 border border-accent/30 mb-3 shadow-[0_0_15px_rgba(59,130,246,0.3)]">
                <svg className="h-7 w-7 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.8}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <p className="text-sm font-semibold text-white mb-1">SOC Threat Intelligence Analyst Ready</p>
              <p className="text-xs text-muted max-w-md mx-auto">
                Ask any cybersecurity question — threat analysis, MITRE ATT&amp;CK, IOC investigation, incident containment, or Sigma rules. Operating with 100% availability.
              </p>
            </div>

            {/* Quick Prompts */}
            <div>
              <p className="text-[0.6875rem] text-faint uppercase tracking-wider font-semibold mb-2">
                Suggested Analyst Queries
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {QUICK_PROMPTS.map((p, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(p)}
                    disabled={loading}
                    className="text-left px-3 py-2 rounded-lg border border-line/80 bg-raised/50 hover:bg-panel hover:border-cyan text-xs text-muted hover:text-ink transition-all cursor-pointer disabled:opacity-50"
                  >
                    ⚡ {p}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
            {/* Avatar */}
            <div
              className={`flex-shrink-0 h-7 w-7 rounded-full flex items-center justify-center text-[0.65rem] font-bold ${
                m.role === "user" ? "bg-accent text-white" : "bg-gradient-to-br from-accent to-cyan text-white shadow-[0_0_8px_rgba(6,182,212,0.6)]"
              }`}
            >
              {m.role === "user" ? "U" : "AI"}
            </div>

            {/* Bubble */}
            <div
              className={`max-w-[85%] rounded-xl px-4 py-3 space-y-1 shadow-glass ${
                m.role === "user"
                  ? "bg-accent/20 border border-accent/30 text-ink"
                  : "bg-panel border border-line/70 text-ink"
              }`}
            >
              {m.role === "model" ? (
                <div className="space-y-1">{formatText(m.text)}</div>
              ) : (
                <p className="text-xs text-ink">{m.text}</p>
              )}
              {m.ts && (
                <p className="text-[0.6rem] text-faint pt-1">
                  {new Date(m.ts).toLocaleTimeString()}
                </p>
              )}
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex gap-3">
            <div className="flex-shrink-0 h-7 w-7 rounded-full bg-gradient-to-br from-accent to-cyan flex items-center justify-center text-[0.65rem] font-bold text-white shadow-[0_0_8px_rgba(6,182,212,0.6)]">
              AI
            </div>
            <div className="bg-panel border border-line/60 rounded-xl px-4 py-3 flex items-center gap-2">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="h-1.5 w-1.5 rounded-full bg-cyan animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </div>
              <span className="text-xs text-muted font-mono">Analyzing threat vectors and MITRE playbooks…</span>
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
      <div className="px-6 pb-5 pt-3 border-t border-line/60 bg-panel/40 backdrop-blur-md">
        <div className="relative flex gap-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            rows={2}
            placeholder="Ask about threats, MITRE ATT&CK, containment playbooks, IOCs, Sigma rules... (Enter to send, Shift+Enter for newline)"
            className="flex-1 resize-none rounded-xl border border-line/80 bg-raised/70 px-4 py-3 text-sm text-ink placeholder:text-faint transition-all focus:border-cyan focus:bg-elevated focus:outline-none focus:ring-1 focus:ring-cyan disabled:opacity-50 font-mono"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={loading || !input.trim()}
            className="self-end px-4 py-3 rounded-xl bg-cyan text-black font-bold text-sm hover:bg-cyan/80 transition-all shadow-[0_0_12px_rgba(6,182,212,0.4)] cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <span className="h-4 w-4 rounded-full border-2 border-black/40 border-t-black animate-spin" />
            ) : (
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
        <div className="flex items-center justify-between mt-2">
          <p className="text-[0.625rem] font-mono text-faint">
            {effectiveKey
              ? "⚡ Connected to Google Gemini 2.0 Flash Live API"
              : "🛡️ Running Built-in SOC Threat Intelligence Reasoning Engine (Zero external dependencies)"}
          </p>
          {messages.length > 0 && (
            <button
              onClick={() => {
                setMessages([]);
                setError(null);
                setNotice(null);
              }}
              className="text-[0.6rem] text-faint hover:text-muted cursor-pointer"
            >
              Clear chat
            </button>
          )}
        </div>
      </div>

      {/* Modal for Setting / Testing Gemini API Key */}
      {keyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-md rounded-2xl border border-line bg-panel p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>🔑</span> Google Gemini AI Configuration
              </h3>
              <button onClick={() => setKeyModal(false)} className="text-muted hover:text-white text-sm">
                ✕
              </button>
            </div>
            <p className="text-xs text-muted leading-relaxed">
              Connect a free Google AI Studio API key (starts with <code className="text-cyan font-mono">AIza...</code>) to enable live Gemini 2.0 Flash reasoning. If omitted, the platform seamlessly uses its high-speed <strong>Built-in SOC Threat Intelligence Engine</strong>.
            </p>
            <div>
              <label className="block text-[0.6875rem] font-mono text-muted mb-1">
                API Key (Google AI Studio)
              </label>
              <input
                type="password"
                value={keyInput}
                onChange={(e) => setKeyInput(e.target.value)}
                placeholder="AIzaSy..."
                className="w-full rounded-lg border border-line bg-raised px-3 py-2 text-xs font-mono text-white focus:border-cyan focus:outline-none"
              />
            </div>

            {keyTestStatus.message && (
              <div
                className={`p-2 rounded text-xs font-mono ${
                  keyTestStatus.success === true
                    ? "bg-ok/10 border border-ok/40 text-ok"
                    : keyTestStatus.success === false
                    ? "bg-sev-critical/10 border border-sev-critical/40 text-sev-critical"
                    : "bg-raised text-muted"
                }`}
              >
                {keyTestStatus.testing ? "⏳ " : keyTestStatus.success ? "✓ " : "✕ "}
                {keyTestStatus.message}
              </div>
            )}

            <div className="pt-2 border-t border-line/60 flex items-center justify-between">
              <a
                href="https://aistudio.google.com/apikey"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[0.6875rem] text-cyan hover:underline font-mono"
              >
                Get Free API Key ↗
              </a>
              <div className="flex gap-2">
                {effectiveKey && (
                  <button
                    onClick={handleClearKey}
                    className="px-3 py-1.5 rounded-lg border border-sev-critical/40 text-xs font-mono text-sev-critical hover:bg-sev-critical/10 cursor-pointer"
                  >
                    Clear Key
                  </button>
                )}
                <button
                  onClick={handleTestKey}
                  disabled={keyTestStatus.testing || !keyInput.trim()}
                  className="px-3 py-1.5 rounded-lg border border-line text-xs font-mono text-muted hover:text-white cursor-pointer disabled:opacity-40"
                >
                  {keyTestStatus.testing ? "Testing..." : "Test Key"}
                </button>
                <button
                  onClick={handleSaveKey}
                  className="px-4 py-1.5 rounded-lg bg-cyan text-black text-xs font-mono font-bold hover:bg-cyan/80 cursor-pointer"
                >
                  Save Key
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
