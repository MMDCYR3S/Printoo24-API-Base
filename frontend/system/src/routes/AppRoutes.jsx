import React from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import Login from "@/features/auth/pages/Login";
import DashboardLayout from "@/components/layout/DashboardLayout";
import useAuthStore from "@/store/authStore";

import AdminRoutes from "@/features/roles/admin/routes/AdminRoutes";
import DesignRoutes from "@/features/roles/design/routes/DesignRoutes";
import PrintRoutes from "@/features/roles/print/routes/PrintRoutes";
import FinancialRoutes from "@/features/roles/financial/routes/FinancialRoutes";
import LogisticsRoutes from "@/features/roles/logistics/routes/LogisticsRoutes";

const AuthGuard = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }
  return children;
};

// گارد امنیتی مبتنی بر نقش (با کلید دقیق بک‌اند)
const RoleGuard = ({ allowedRoles, children }) => {
  const { user } = useAuthStore();
  const role = user?.role || "admin"; 

  if (!allowedRoles.includes(role)) {
    return <Navigate to={`/${role}`} replace />;
  }
  return children;
};

export default function AppRoutes() {
  const { user } = useAuthStore();
  const role = user?.role || "admin";

  return (
    <Routes>
      <Route path="/auth/login" element={<Login />} />
      
      <Route
        path="/*"
        element={
          <AuthGuard>
            <DashboardLayout>
              <Routes>
                <Route path="admin/*" element={<RoleGuard allowedRoles={["admin"]}><AdminRoutes /></RoleGuard>} />
                
                {/* 🔴 کلید دقیق designer ثبت شد */}
                <Route path="designer/*" element={<RoleGuard allowedRoles={["designer", "admin"]}><DesignRoutes /></RoleGuard>} />
                
                <Route path="print/*" element={<RoleGuard allowedRoles={["print", "admin"]}><PrintRoutes /></RoleGuard>} />
                <Route path="financial/*" element={<RoleGuard allowedRoles={["financial", "admin"]}><FinancialRoutes /></RoleGuard>} />
                <Route path="logistics/*" element={<RoleGuard allowedRoles={["logistics", "admin"]}><LogisticsRoutes /></RoleGuard>} />
                
                <Route path="/" element={<Navigate to={`/${role}`} replace />} />
                <Route path="*" element={<Navigate to={`/${role}`} replace />} />
              </Routes>
            </DashboardLayout>
          </AuthGuard>
        }
      />
    </Routes>
  );
}