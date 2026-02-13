import React, { useState } from "react";
import { Outlet, Navigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import Header from "./Header";
import Sidebar from "./Sidebar";
import useAuthStore from "@/store/authStore";

// ایمپورت کانفیگ‌های ادمین
import { adminNavigation } from "@/features/roles/admin/config/adminNavigation";
import { adminHeaderActions } from "@/features/roles/admin/config/adminHeaderActions";

export default function DashboardLayout() {
  const { user, isAuthenticated, isLoading } = useAuthStore();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  if (isLoading) return null;
  if (!isAuthenticated) return <Navigate to="/auth/login" replace />;

  // تخصیص منو و اکشن‌ها
  const navigationItems = adminNavigation;
  const headerActions = adminHeaderActions;

  return (
    <div className="min-h-screen bg-gray-dark flex flex-col" dir="rtl">
      {/* پاس دادن دکمه‌های هدر */}
      <Header actions={headerActions} />
      
      <Sidebar 
        items={navigationItems} 
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <main 
        className={cn(
          "flex-1 pt-20 pb-8 transition-all duration-300 ease-in-out min-h-screen bg-gray-50", 
          sidebarCollapsed ? "pr-20" : "pr-72", 
          "pl-4 sm:pl-8"
        )}
      >
        <div className="container mx-auto max-w-7xl animate-in fade-in slide-in-from-bottom-4 duration-500">
          <Outlet />
        </div>
      </main>
    </div>
  );
}