import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
// مسیرها رو بر اساس پوشه‌بندیت چک کن
import LogisticsDashboard from "../features/dashboard/pages/LogisticsDashboard";
import LogisticsOrderList from "../features/orderList/pages/LogisticsOrderList";
import LogisticsOrderDetail from "../features/orderDetail/pages/LogisticsOrderDetail";

export default function LogisticsRoutes() {
  return (
    <Routes>
      <Route path="dashboard" element={<LogisticsDashboard />} />
      <Route path="orders" element={<LogisticsOrderList />} />
      <Route path="orders/detail/:id" element={<LogisticsOrderDetail />} />
      
      {/* 🔴 ریدایرکت با آدرس مطلق برای شکستن لوپ بی‌نهایت */}
      <Route path="*" element={<Navigate to="/logistics/dashboard" replace />} />
    </Routes>
  );
}