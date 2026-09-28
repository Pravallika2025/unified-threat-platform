import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { endpoints, getRegisteredUsers, setMockMode } from "@/lib/api/endpoints";
import { tokenStore } from "@/lib/api/client";
import type { PermissionKey } from "@/lib/rbac/permissions";
import type { Me, User } from "@/types/api";
import { MOCK_ADMIN, MOCK_ANALYST, MOCK_TOKENS } from "@/lib/api/mockData";

interface AuthValue {
  user: Me | null;
  loading: boolean;
  signIn: (email: string, password: string, totp?: string) => Promise<void>;
  loginDemo: (role?: "admin" | "analyst") => void;
  loginRegisteredUser: (user: User | Me) => void;
  signOut: () => void;
  can: (permission: PermissionKey) => boolean;
}

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);

  const loginRegisteredUser = useCallback((userProfile: User | Me) => {
    setMockMode(true, userProfile.role === "super_admin" ? "admin" : "analyst");
    tokenStore.save(MOCK_TOKENS);
    localStorage.setItem("tp.current_user_email", userProfile.email);
    localStorage.setItem("tp.mock_user_role", userProfile.role === "super_admin" ? "admin" : "analyst");
    
    const meObj: Me = {
      id: userProfile.id,
      email: userProfile.email,
      full_name: userProfile.full_name,
      role: userProfile.role,
      environment_id: userProfile.environment_id,
      is_active: userProfile.is_active,
      mfa_enabled: userProfile.mfa_enabled,
      permissions:
        "permissions" in userProfile && Array.isArray(userProfile.permissions)
          ? userProfile.permissions
          : userProfile.role === "super_admin"
            ? MOCK_ADMIN.permissions
            : MOCK_ANALYST.permissions,
    };
    setUser(meObj);
    setLoading(false);
  }, []);

  const loginDemo = useCallback((role: "admin" | "analyst" = "admin") => {
    setMockMode(true, role);
    tokenStore.save(MOCK_TOKENS);
    const mockUser = role === "analyst" ? MOCK_ANALYST : MOCK_ADMIN;
    localStorage.setItem("tp.current_user_email", mockUser.email);
    localStorage.setItem("tp.mock_user_role", role);
    setUser(mockUser);
    setLoading(false);
  }, []);

  useEffect(() => {
    const savedRole = localStorage.getItem("tp.mock_user_role") as "admin" | "analyst" | null;
    const isMock = localStorage.getItem("tp.mock_mode") === "true";
    const currentEmail = localStorage.getItem("tp.current_user_email");

    if (isMock && currentEmail) {
      const registered = getRegisteredUsers().find(
        (u) => u.email.toLowerCase() === currentEmail.toLowerCase(),
      );
      if (registered) {
        setUser({
          id: registered.id,
          email: registered.email,
          full_name: registered.full_name,
          role: registered.role,
          environment_id: registered.environment_id,
          is_active: registered.is_active,
          mfa_enabled: registered.mfa_enabled,
          permissions: registered.role === "super_admin" ? MOCK_ADMIN.permissions : MOCK_ANALYST.permissions,
        });
        setLoading(false);
        return;
      }
    }

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
      localStorage.setItem("tp.current_user_email", email);
      const profile = await endpoints.me();
      setUser(profile);
    } catch (err) {
      console.info("Fallback to SOC Sandbox mode:", err);
      // Check if email matches a registered user in local store
      const registered = getRegisteredUsers().find(
        (u) => u.email.toLowerCase() === email.toLowerCase(),
      );
      if (registered) {
        loginRegisteredUser(registered);
        return;
      }
      const role = email.toLowerCase().includes("analyst") ? "analyst" : "admin";
      loginDemo(role);
    }
  }, [loginDemo, loginRegisteredUser]);

  const signOut = useCallback(() => {
    tokenStore.clear();
    setMockMode(false);
    localStorage.removeItem("tp.current_user_email");
    localStorage.removeItem("tp.mock_user_role");
    setUser(null);
  }, []);

  const can = useCallback(
    (permission: PermissionKey) => user?.permissions.includes(permission) ?? false,
    [user],
  );

  const value = useMemo(
    () => ({ user, loading, signIn, loginDemo, loginRegisteredUser, signOut, can }),
    [user, loading, signIn, loginDemo, loginRegisteredUser, signOut, can],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
