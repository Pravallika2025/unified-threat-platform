import type { Config } from "tailwindcss";

/**
 * Palette is operational, not decorative: severity colours are the same five
 * values everywhere (chart, badge, border, chip) so an analyst reads urgency by
 * hue alone without checking a legend.
 */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ground: "#0A1017",
        panel: "#111A24",
        raised: "#16212D",
        line: "#1F2C3A",
        ink: "#E6EDF3",
        muted: "#7C8DA0",
        faint: "#4A5B6E",
        accent: "#4C8DFF",
        sev: {
          critical: "#FF4D6D",
          high: "#FF9F43",
          medium: "#FFD166",
          low: "#4CC9F0",
          info: "#7C8DA0",
        },
        ok: "#2DD4A7",
      },
      fontFamily: {
        // No web fonts: the platform must run on an air-gapped internal network.
        sans: ["Inter", "ui-sans-serif", "system-ui", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
      },
      fontSize: {
        eyebrow: ["0.6875rem", { lineHeight: "1rem", letterSpacing: "0.08em" }],
      },
    },
  },
  plugins: [],
} satisfies Config;
