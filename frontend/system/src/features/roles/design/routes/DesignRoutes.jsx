import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import DesignDashboard from "../features/dashboard/pages/DesignDashboard";
import DesignOrderList from "../features/orderList/pages/DesignOrderList";
import DesignOrderDetail from "../features/orderDetail/pages/DesignOrderDetail";

export default function DesignRoutes() {
  return (
    <Routes>
      <Route path="designDashboard" element={<DesignDashboard />} />
      <Route path="orders" element={<DesignOrderList />} />
      <Route path="orders/detail/:id" element={<DesignOrderDetail />} />
      
      <Route path="*" element={<Navigate to="designDashboard" replace />} />
    </Routes>
  );
}