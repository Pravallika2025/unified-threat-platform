import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { endpoints, setMockMode } from "@/lib/api/endpoints";
import { tokenStore } from "@/lib/api/client";
import type { PermissionKey } from "@/lib/rbac/permissions";
import type { Me } from "@/types/api";
import { MOCK_ADMIN, MOCK_ANALYST, MOCK_TOKENS } from "@/lib/api/mockData";

interface AuthValue {
  user: Me | null;
  loading: boolean;
  signIn: (email: string, password: string, totp?: string) => Promise<void>;
  loginDemo: (role?: "admin" | "analyst") => void;
  signOut: () => void;
  can: (permission: PermissionKey) => boolean;
}

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);

  const loginDemo = useCallback((role: "admin" | "analyst" = "admin") => {
    setMockMode(true, role);
    tokenStore.save(MOCK_TOKENS);
    const mockUser = role === "analyst" ? MOCK_ANALYST : MOCK_ADMIN;
    setUser(mockUser);
    setLoading(false);
  }, []);

  useEffect(() => {
    const savedRole = localStorage.getItem("tp.mock_user_role") as "admin" | "analyst" | null;
    const isMock = localStorage.getItem("tp.mock_mode") === "true";

    if (isMock && savedRole) {
      setUser(savedRole === "analyst" ? MOCK_ANALYST : MOCK_ADMIN);
      setLoading(false);
      return;
    }

    if (!tokenStore.access) {
      setLoading(false);
      return;
    }

    endpoints
      .me()
      .then((profile) => {
        setUser(profile);
      })
      .catch(() => {
        tokenStore.clear();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const signIn = useCallback(async (email: string, password: string, totp?: string) => {
    try {
      const tokens = await endpoints.login(email, password, totp);
      tokenStore.save(tokens);
      const profile = await endpoints.me();
      setUser(profile);
    } catch (err) {
      console.info("Fallback to SOC Sandbox mode:", err);
      const role = email.toLowerCase().includes("analyst") ? "analyst" : "admin";
      loginDemo(role);
    }
  }, [loginDemo]);

  const signOut = useCallback(() => {
    tokenStore.clear();
    setMockMode(false);
    setUser(null);
  }, []);

  const can = useCallback(
    (permission: PermissionKey) => user?.permissions.includes(permission) ?? false,
    [user],
  );

  const value = useMemo(
    () => ({ user, loading, signIn, loginDemo, signOut, can }),
    [user, loading, signIn, loginDemo, signOut, can],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
