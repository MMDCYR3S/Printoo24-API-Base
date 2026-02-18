import React, { useState } from "react";
import { Navigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import Header from "./Header";
import Sidebar from "./Sidebar";
import useAuthStore from "@/store/authStore";

// ایمپورت کانفیگ‌های نویگیشن
import { adminNavigation } from "@/features/roles/admin/config/adminNavigation";
import { adminHeaderActions } from "@/features/roles/admin/config/adminHeaderActions";
import { designNavigation } from "@/features/roles/design/config/designNavigation";
import { printNavigation } from "@/features/roles/print/config/printNavigation";
import { logisticsNavigation } from "@/features/roles/logistics/config/logisticsNavigation";
import { financialNavigation } from "@/features/roles/financial/config/financialNavigation";


// تنظیمات نقش‌ها (دقیقاً با کلیدهای بک‌اند)
const roleConfigs = {
  admin: {
    navigation: adminNavigation,
    actions: adminHeaderActions,
  },
  // 🔴 کلید دقیق طراح طبق بک‌ند
  designer: {
    navigation: designNavigation,
    actions: [], 
  },
print: { 
    navigation: printNavigation, 
    actions: [] 
  },
financial: { 
    navigation: financialNavigation, 
    actions: [] 
  },
logistics: {
    navigation: logisticsNavigation,
    actions: [],
  },
};

export default function DashboardLayout({ children }) {
  const { isAuthenticated, isLoading, user } = useAuthStore();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const SIDEBAR_WIDTH = "280px"; 
  const SIDEBAR_COLLAPSED_WIDTH = "80px";

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-gray-dark">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold-light"></div>
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/auth/login" replace />;

  // 🔴 خواندن مستقیم نقش کاربر بدون مپر (با پیش‌فرض admin)
  const currentRole = user?.role || "admin";
  
  // پیدا کردن تنظیمات مربوط به نقش (اگر پیدا نکرد، ادمین رو نشون میده)
  const currentConfig = roleConfigs[currentRole] || roleConfigs.admin;
  const navigationItems = currentConfig.navigation;
  const headerActions = currentConfig.actions;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col" dir="rtl">
      <Header actions={headerActions} />
      
      <Sidebar 
        items={navigationItems} 
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        className="fixed right-0 top-0 h-full z-40 transition-all duration-300"
      />

      <main 
        className={cn(
          "flex-1 pt-20 pb-8 min-h-screen transition-all duration-300 ease-in-out"
        )}
        style={{
           marginRight: sidebarCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH
        }}
      >
        <div className="w-full px-4 md:px-6 lg:px-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {children} 
        </div>
      </main>
    </div>
  );
}