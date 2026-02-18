import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import DesignDashboard from "../features/dashboard/pages/DesignDashboard";
import DesignOrderList from "../features/orderList/pages/DesignOrderList";
import DesignOrderDetail from "../features/orderDetail/pages/DesignOrderDetail";

export default function DesignRoutes() {
  return (
    <Routes>
      <Route path="dashboard" element={<DesignDashboard />} />
      <Route path="orders" element={<DesignOrderList />} />
      <Route path="orders/detail/:id" element={<DesignOrderDetail />} />
      
      {/* 🔴 استفاده از آدرس مطلق برای جلوگیری از لوپ بی‌نهایت */}
      <Route path="*" element={<Navigate to="/designer/dashboard" replace />} />
    </Routes>
  );
}