import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
// مسیر ایمپورت‌ها رو بر اساس پوشه‌بندی خودت چک کن (احتمالا همین‌هاست)
import PrintDashboard from "../features/dashboard/pages/PrintDashboard";
import PrintOrderList from "../features/orderList/pages/PrintOrderList";
import PrintOrderDetail from "../features/orderDetail/pages/PrintOrderDetail";

export default function PrintRoutes() {
  return (
    <Routes>
      <Route path="dashboard" element={<PrintDashboard />} />
      <Route path="orders" element={<PrintOrderList />} />
      <Route path="orders/detail/:id" element={<PrintOrderDetail />} />
      
      {/* ریدایرکت با آدرس مطلق برای جلوگیری از لوپ بی‌نهایت */}
      <Route path="*" element={<Navigate to="/print/dashboard" replace />} />
    </Routes>
  );
}