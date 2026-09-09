import { Navigate, Route, Routes } from "react-router-dom";

import { Shell } from "@/components/layout/Shell";
import { Loading } from "@/components/ui";
import { AlertsPage } from "@/features/alerts/AlertsPage";
import { AuditPage } from "@/features/audit/AuditPage";
import { LoginPage } from "@/features/auth/LoginPage";
import { RegisterPage } from "@/features/auth/RegisterPage";
import { EnvironmentsPage } from "@/features/environments/EnvironmentsPage";
import { IncidentDetailPage } from "@/features/incidents/IncidentDetailPage";
import { IncidentsPage } from "@/features/incidents/IncidentsPage";
import { LiveMonitorPage } from "@/features/live/LiveMonitorPage";
import { OverviewPage } from "@/features/overview/OverviewPage";
import { ReportsPage } from "@/features/reports/ReportsPage";
import { ReviewQueuePage } from "@/features/review/ReviewQueuePage";
import { ThreatIntelPage } from "@/features/threat_intel/ThreatIntelPage";
import { UploadPage } from "@/features/upload/UploadPage";
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
      <Route path="/register" element={<RegisterPage />} />
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
        <Route path="threat-intel" element={<ThreatIntelPage />} />
        <Route path="review" element={<ReviewQueuePage />} />
        <Route path="environments" element={<EnvironmentsPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="audit" element={<AuditPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
