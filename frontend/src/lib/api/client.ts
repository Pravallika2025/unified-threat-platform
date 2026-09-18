import type { Tokens } from "@/types/api";

const BASE = import.meta.env.VITE_API_URL ?? "";
const PREFIX = `${BASE}/api/v1`;

const ACCESS_KEY = "tp.access";
const REFRESH_KEY = "tp.refresh";

export const tokenStore = {
  get access() {
    return localStorage.getItem(ACCESS_KEY);
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY);
  },
  save(tokens: Tokens) {
    localStorage.setItem(ACCESS_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

/** The backend returns problem+json; surface its title so the UI never shows "Error: 400". */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public detail?: unknown,
  ) {
    super(message);
  }
}

async function parseError(response: Response): Promise<ApiError> {
  let message = response.statusText || "Request failed";
  let detail: unknown;
  try {
    const body = await response.json();
    message = body.title ?? body.detail?.[0]?.msg ?? body.detail ?? message;
    detail = body.detail;
  } catch {
    /* non-JSON error body */
  }
  return new ApiError(response.status, String(message), detail);
}

let refreshing: Promise<boolean> | null = null;

async function tryRefresh(): Promise<boolean> {
  const refresh = tokenStore.refresh;
  if (!refresh) return false;

  // Collapse concurrent 401s into a single refresh attempt.
  refreshing ??= (async () => {
    try {
      const response = await fetch(
        `${PREFIX}/auth/refresh?refresh_token=${encodeURIComponent(refresh)}`,
        { method: "POST" },
      );
      if (!response.ok) return false;
      tokenStore.save(await response.json());
      return true;
    } catch {
      return false;
    } finally {
      refreshing = null;
    }
  })();

  return refreshing;
}

async function request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(init.headers);
  if (!(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const access = tokenStore.access;
  if (access) headers.set("Authorization", `Bearer ${access}`);

  let response: Response;
  try {
    response = await fetch(`${PREFIX}${path}`, { ...init, headers });
  } catch (err) {
    throw new ApiError(0, "Cannot reach backend server. Please verify backend is running on port 8000.", err);
  }

  if (response.status === 401 && retry && (await tryRefresh())) {
    return request<T>(path, init, false);
  }
  if (response.status === 401) {
    tokenStore.clear();
    window.location.assign("/login");
    throw new ApiError(401, "Your session has expired. Sign in again.");
  }
  if (!response.ok) throw await parseError(response);
  if (response.status === 204) return undefined as T;

  const contentType = response.headers.get("content-type") ?? "";
  return (contentType.includes("json") ? response.json() : response.text()) as Promise<T>;
}

export const api = {
  get: <T>(path: string, options?: RequestInit) => request<T>(path, { ...options, method: "GET" }),
  post: <T>(path: string, body?: unknown, options?: RequestInit) =>
    request<T>(path, {
      ...options,
      method: "POST",
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
  upload: <T>(path: string, form: FormData) =>
    request<T>(path, { method: "POST", body: form }),
  download: async (path: string, fallbackFilename: string) => {
    const headers = new Headers();
    const access = tokenStore.access;
    if (access) headers.set("Authorization", `Bearer ${access}`);
    const response = await fetch(`${PREFIX}${path}`, { headers });
    if (!response.ok) throw await parseError(response);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const disposition = response.headers.get("content-disposition");
    let filename = fallbackFilename;
    if (disposition && disposition.includes("filename=")) {
      const match = disposition.match(/filename="?([^"]+)"?/);
      if (match && match[1]) filename = match[1];
    }
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },
};
