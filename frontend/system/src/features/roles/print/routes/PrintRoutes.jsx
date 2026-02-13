import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import PrintDashboard from "../features/dashboard/pages/PrintDashboard";
import PrintOrderList from "../features/orderList/pages/PrintOrderList";
import PrintOrderDetail from "../features/orderDetail/pages/PrintOrderDetail";

export default function PrintRoutes() {
  return (
    <Routes>
      <Route path="printDashboard" element={<PrintDashboard />} />
      <Route path="orders" element={<PrintOrderList />} />
      <Route path="orders/detail/:id" element={<PrintOrderDetail />} />
      
      <Route path="*" element={<Navigate to="printDashboard" replace />} />
    </Routes>
  );
}