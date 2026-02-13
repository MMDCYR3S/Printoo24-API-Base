import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import LogisticsDashboard from "../features/dashboard/pages/LogisticsDashboard";
import LogisticsOrderList from "../features/orderList/pages/LogisticsOrderList";
import LogisticsOrderDetail from "../features/orderDetail/pages/LogisticsOrderDetail.jsx";

export default function LogisticsRoutes() {
  return (
    <Routes>
      <Route path="logisticsDashboard" element={<LogisticsDashboard />} />
      <Route path="orders" element={<LogisticsOrderList />} />
      <Route path="orders/detail/:id" element={<LogisticsOrderDetail />} />
      
      <Route path="*" element={<Navigate to="logisticsDashboard" replace />} />
    </Routes>
  );
}