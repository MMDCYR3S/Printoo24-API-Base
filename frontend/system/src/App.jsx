// src/App.jsx (Final Version)
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner"; 

import DashboardLayout from "./components/layout/DashboardLayout";
import OrdersPage from "./features/orders/pages/OrdersPage";
import Login from "./features/auth/pages/Login"; 
import ProtectedRoute from "./components/shared/ProtectedRoute";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* مسیر عمومی لاگین */}
          <Route path="/login" element={<Login />} />

          {/* مسیرهای محافظت شده */}
          <Route path="/" element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Navigate to="/orders" replace />} />
            <Route path="orders" element={<OrdersPage />} />
            {/* بقیه روت‌ها اینجا اضافه می‌شوند */}
          </Route>
        </Routes>
      </Router>
      <Toaster position="top-center" richColors />
    </QueryClientProvider>
  );
}

export default App;