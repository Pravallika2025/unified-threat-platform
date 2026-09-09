import type { Config } from "tailwindcss";

/**
 * Modern High-End SOC Defense Theme
 * Operational palette with high-contrast cyber dark aesthetics, glassmorphism, and neon glow accents.
 */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        ground: "#070B11",
        surface: "#0B111A",
        panel: "#0F1724",
        raised: "#141F30",
        elevated: "#1A283D",
        line: "#1E2E44",
        lineHover: "#2A3F5C",
        ink: "#F0F6FC",
        muted: "#8B9BB4",
        faint: "#4E6078",
        accent: "#3B82F6",
        accentHover: "#60A5FA",
        cyan: "#06B6D4",
        sev: {
          critical: "#FF385C",
          high: "#F97316",
          medium: "#FBBF24",
          low: "#38BDF8",
          info: "#8B9BB4",
        },
        ok: "#10B981",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
      },
      fontSize: {
        eyebrow: ["0.6875rem", { lineHeight: "1rem", letterSpacing: "0.1em" }],
      },
      boxShadow: {
        "glow-accent": "0 0 20px -3px rgba(59, 130, 246, 0.4)",
        "glow-critical": "0 0 20px -3px rgba(255, 56, 92, 0.4)",
        "glow-ok": "0 0 20px -3px rgba(16, 185, 129, 0.4)",
        "glow-medium": "0 0 20px -3px rgba(251, 191, 36, 0.35)",
        "glass": "0 8px 32px 0 rgba(0, 0, 0, 0.4)",
      },
      backgroundImage: {
        "radial-grid": "radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.04) 0%, transparent 100%)",
        "cyber-gradient": "linear-gradient(135deg, rgba(15, 23, 36, 0.9) 0%, rgba(11, 17, 26, 0.95) 100%)",
        "accent-gradient": "linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "beacon": "beacon 2s cubic-bezier(0, 0, 0.2, 1) infinite",
      },
      keyframes: {
        beacon: {
          "0%": { transform: "scale(0.95)", opacity: "0.8" },
          "70%": { transform: "scale(1.9)", opacity: "0" },
          "100%": { transform: "scale(1.9)", opacity: "0" },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
