import React, { useState } from "react";
import { Navigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import Header from "./Header";
import Sidebar from "./Sidebar";
import useAuthStore from "@/store/authStore";

import { adminNavigation } from "@/features/roles/admin/config/adminNavigation";
import { adminHeaderActions } from "@/features/roles/admin/config/adminHeaderActions";

export default function DashboardLayout({ children }) {
  const { isAuthenticated, isLoading } = useAuthStore();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // عرض سایدبار را اینجا تعریف می‌کنیم تا هماهنگی کامل باشد
  // نکته: این مقادیر باید با عرض واقعی کامپوننت Sidebar شما یکی باشد
  const SIDEBAR_WIDTH = "280px"; 
  const SIDEBAR_COLLAPSED_WIDTH = "80px"; // عرض در حالت بسته (فقط آیکون)

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
    <div className="min-h-screen bg-gray-50 flex flex-col" dir="rtl">
      {/* هدر: اگر هدر شما روی سایدبار می‌افتد z-index بالا بدهید */}
      <Header actions={headerActions} />
      
      {/* سایدبار */}
      <Sidebar 
        items={navigationItems} 
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        // احتمالا باید عرض را به خود سایدبار هم پاس بدهید یا در آنجا ثابت باشد
        className="fixed right-0 top-0 h-full z-40 transition-all duration-300"
      />

      {/* محتوای اصلی */}
      <main 
        className={cn(
          "flex-1 pt-20 pb-8 min-h-screen transition-all duration-300 ease-in-out",
          // منطق اصلی پر شدن صفحه اینجاست:
          // بر اساس وضعیت سایدبار، مارجین راست را تغییر می‌دهیم
        )}
        style={{
           marginRight: sidebarCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH
        }}
      >
        {/* حذف container و max-w-7xl برای استفاده از تمام عرض صفحه 
            استفاده از w-full و p-4 یا p-6 برای فاصله مناسب از لبه‌ها
        */}
        <div className="w-full px-4 md:px-6 lg:px-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {children} 
        </div>
      </main>
    </div>
  );
}