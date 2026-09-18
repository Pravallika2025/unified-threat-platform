import type { ReactNode } from "react";
import { BrowserRouter } from "react-router-dom";

import { AuthProvider } from "@/lib/auth/AuthContext";

export function Providers({ children }: { children: ReactNode }) {
  const basename = (import.meta.env.BASE_URL || "/").replace(/\/$/, "");
  return (
    <BrowserRouter basename={basename}>
      <AuthProvider>{children}</AuthProvider>
    </BrowserRouter>
  );
}
