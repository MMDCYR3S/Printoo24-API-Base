import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

// ایمپورت صفحات دپارتمان مالی
import FinancialDashboard from "../features/dashboard/pages/FinancialDashboard";
import FinancialOrderList from "../features/orderList/pages/FinancialOrderList";
import FinancialOrderDetail from "../features/orderDetail/pages/FinancialOrderDetail";
import PendingCosts from "../features/pendingTransactions/pages/PendingCosts";
import Transactions from "../features/transactions/pages/Transactions";
import TransactionDetail from "../features/transactionDetail/pages/TransactionDetail";

export default function FinancialRoutes() {
  return (
    <Routes>
      <Route path="dashboard" element={<FinancialDashboard />} />
      <Route path="orders" element={<FinancialOrderList />} />
      <Route path="orders/detail/:id" element={<FinancialOrderDetail />} />
      <Route path="pending-transactions" element={<PendingCosts />} />
      <Route path="transactions" element={<Transactions />} />
      <Route path="transactions/detail/:id" element={<TransactionDetail />} />
      
      {/* 🔴 ریدایرکت با آدرس مطلق برای جلوگیری از لوپ بی‌نهایت */}
      <Route path="*" element={<Navigate to="/financial/dashboard" replace />} />
    </Routes>
  );
}