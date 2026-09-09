import { Navigate, Route, Routes } from "react-router-dom";

import { Shell } from "@/components/layout/Shell";
import { Loading } from "@/components/ui";
import { AlertsPage } from "@/features/alerts/AlertsPage";
import { AuditPage } from "@/features/audit/AuditPage";
import { LoginPage } from "@/features/auth/LoginPage";
import { EnvironmentsPage } from "@/features/environments/EnvironmentsPage";
import { IncidentDetailPage } from "@/features/incidents/IncidentDetailPage";
import { IncidentsPage } from "@/features/incidents/IncidentsPage";
import { LiveMonitorPage } from "@/features/live/LiveMonitorPage";
import { OverviewPage } from "@/features/overview/OverviewPage";
import { ReviewQueuePage } from "@/features/review/ReviewQueuePage";
import { UsersPage } from "@/features/users/UsersPage";
import { useAuth } from "@/lib/auth/AuthContext";

function RequireAuth({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) return <Loading label="Checking your session" />;
  return user ? children : <Navigate to="/login" replace />;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RequireAuth>
            <Shell />
          </RequireAuth>
        }
      >
        <Route index element={<OverviewPage />} />
        <Route path="live" element={<LiveMonitorPage />} />
        <Route path="incidents" element={<IncidentsPage />} />
        <Route path="incidents/:id" element={<IncidentDetailPage />} />
        <Route path="alerts" element={<AlertsPage />} />
        <Route path="review" element={<ReviewQueuePage />} />
        <Route path="environments" element={<EnvironmentsPage />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="audit" element={<AuditPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
