import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { endpoints } from "@/lib/api/endpoints";
import { setMockMode } from "@/lib/api/endpoints";
import { tokenStore } from "@/lib/api/client";
import type { PermissionKey } from "@/lib/rbac/permissions";
import type { Me } from "@/types/api";
import { MOCK_ADMIN, MOCK_ANALYST } from "@/lib/api/mockData";

interface AuthValue {
  user: Me | null;
  loading: boolean;
  signIn: (email: string, password: string, totp?: string) => Promise<void>;
  signOut: () => void;
  can: (permission: PermissionKey) => boolean;
}

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // ── Demo mode (GitHub Pages) ────────────────────────────────────────
    // When the frontend is built for GitHub Pages we ship with an empty
    // VITE_API_URL. In that case we cannot reach a real backend, so we inject
    // a mock user directly and skip the network call.
    if (!import.meta.env.VITE_API_URL) {
      const role = (localStorage.getItem('tp.mock_user_role') as 'admin' | 'analyst') || 'admin';
      const mockUser = role === 'analyst' ? MOCK_ANALYST : MOCK_ADMIN;
      setUser(mockUser);
      setLoading(false);
      setMockMode(true, role);
      return;
    }

    if (!tokenStore.access) {
      setLoading(false);
      return;
    }
    endpoints
      .me()
      .then(setUser)
      .catch(() => tokenStore.clear())
      .finally(() => setLoading(false));
  }, []);

  const signIn = useCallback(async (email: string, password: string, totp?: string) => {
    tokenStore.save(await endpoints.login(email, password, totp));
    setUser(await endpoints.me());
  }, []);

  const signOut = useCallback(() => {
    tokenStore.clear();
    setUser(null);
  }, []);

  const can = useCallback(
    (permission: PermissionKey) => user?.permissions.includes(permission) ?? false,
    [user],
  );

  const value = useMemo(
    () => ({ user, loading, signIn, signOut, can }),
    [user, loading, signIn, signOut, can],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
