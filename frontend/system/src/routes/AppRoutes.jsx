import React from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import Login from "@/features/auth/pages/Login";
import DashboardLayout from "@/components/layout/DashboardLayout";
import useAuthStore from "@/store/authStore";

// ایمپورت روترهای هر نقش
import AdminRoutes from "@/features/roles/admin/routes/AdminRoutes";
import DesignRoutes from "@/features/roles/design/routes/DesignRoutes";
import PrintRoutes from "@/features/roles/print/routes/PrintRoutes";
import FinancialRoutes from "@/features/roles/financial/routes/FinancialRoutes";
import LogisticsRoutes from "@/features/roles/logistics/routes/LogisticsRoutes";

// --- کامپوننت داخلی محافظت از مسیرها (ادغام شده) ---
const AuthGuard = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    // ریدایرکت دقیق به صفحه لاگین تعریف شده
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }
  return children;
};

export default function AppRoutes() {
  const { user } = useAuthStore();
  const role = user?.role || "admin"; // نقش کاربر برای مسیریابی اولیه

  return (
    <Routes>
      {/* مسیرهای عمومی */}
      <Route path="/auth/login" element={<Login />} />
      
      {/* تمام مسیرهای اپلیکیشن تحت نظارت AuthGuard و لایوت اصلی */}
      <Route
        path="/*"
        element={
          <AuthGuard>
            <DashboardLayout>
              <Routes>
                {/* استفاده از /* حیاتی است تا روت‌های داخلی ماژول‌ها 
                   توسط روتر اصلی شناسایی شوند.
                */}
                <Route path="admin/*" element={<AdminRoutes />} />
                <Route path="design/*" element={<DesignRoutes />} />
                <Route path="print/*" element={<PrintRoutes />} />
                <Route path="financial/*" element={<FinancialRoutes />} />
                <Route path="logistics/*" element={<LogisticsRoutes />} />
                
                {/* ریدایرکت هوشمند بر اساس نقش کاربر در بدو ورود */}
                <Route path="/" element={<Navigate to={`/${role}`} replace />} />
                
                {/* مدیریت روت‌های تعریف نشده */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </DashboardLayout>
          </AuthGuard>
        }
      />
    </Routes>
  );
}