import React from "react";
import { Outlet } from "react-router-dom";

export default function DashboardLayout() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* سایدبار موقت */}
      <aside className="w-64 bg-slate-900 text-white hidden md:block">
        <div className="p-6 font-bold text-xl">Printoo Admin</div>
        <nav className="p-4 space-y-2">
          <div className="p-2 bg-slate-800 rounded cursor-pointer">سفارشات</div>
          <div className="p-2 hover:bg-slate-800 rounded cursor-pointer text-slate-300">طراحی</div>
          <div className="p-2 hover:bg-slate-800 rounded cursor-pointer text-slate-300">چاپخانه</div>
        </nav>
      </aside>

      {/* محتوای اصلی */}
      <main className="flex-1">
        <header className="h-16 border-b bg-white flex items-center px-6">
          <span className="font-semibold">پنل مدیریت</span>
        </header>
        <div className="p-4">
          <Outlet /> {/* اینجا OrdersPage رندر می‌شود */}
        </div>
      </main>
    </div>
  );
}