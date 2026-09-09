import type { ReactNode } from "react";

import { useAuth } from "@/lib/auth/AuthContext";
import type { PermissionKey } from "@/lib/rbac/permissions";

/** Hides a control the current role cannot use. The server still enforces it. */
export function Can({
  do: permission,
  children,
  fallback = null,
}: {
  do: PermissionKey;
  children: ReactNode;
  fallback?: ReactNode;
}) {
  return useAuth().can(permission) ? <>{children}</> : <>{fallback}</>;
}
