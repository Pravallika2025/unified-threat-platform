import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  // When deploying to Vercel, the app lives at root "/".
  // When deploying to GitHub Pages, the app lives at "/unified-threat-platform/".
  const isVercel = Boolean(process.env.VERCEL || env.VERCEL || process.env.VERCEL_ENV);
  const base =
    env.VITE_BASE_PATH ??
    (isVercel ? "/" : (command === "build" && !env.VITE_API_URL ? "/unified-threat-platform/" : "/"));

  return {
    base,
    plugins: [react()],
    resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
    server: {
      port: 5173,
      proxy: {
        // The app talks to relative /api paths, so the same build works behind
        // nginx in production without rewriting any URLs.
        "/api": { target: "http://localhost:8000", changeOrigin: true },
        "/ws": { target: "ws://localhost:8000", ws: true },
      },
    },
  };
});
