import React, { useState } from "react";
import { Navigate } from "react-router-dom"; // Outlet حذف شد چون اینجا کاربردی ندارد
import { cn } from "@/lib/utils";
import Header from "./Header";
import Sidebar from "./Sidebar";
import useAuthStore from "@/store/authStore";

import { adminNavigation } from "@/features/roles/admin/config/adminNavigation";
import { adminHeaderActions } from "@/features/roles/admin/config/adminHeaderActions";

// اضافه کردن children به ورودی‌های تابع
export default function DashboardLayout({ children }) {
  const { isAuthenticated, isLoading } = useAuthStore();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-gray-dark">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold-light"></div>
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/auth/login" replace />;

  const navigationItems = adminNavigation;
  const headerActions = adminHeaderActions;

  return (
    <div className="min-h-screen bg-gray-dark flex flex-col" dir="rtl">
      <Header actions={headerActions} />
      
      <Sidebar 
        items={navigationItems} 
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <main 
        className={cn(
          "flex-1 pt-20 pb-8 transition-all duration-300 ease-in-out min-h-screen bg-gray-50", 
          sidebarCollapsed ? "pr-16" : "pr-64", // اصلاح مقادیر برای هماهنگی با عرض سایدبار
          "pl-4 sm:pl-8"
        )}
      >
        <div className="container mx-auto max-w-7xl animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* بخش حیاتی: استفاده از children به جای Outlet */}
          {children} 
        </div>
      </main>
    </div>
  );
}