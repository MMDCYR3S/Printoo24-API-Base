import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import FinancialDashboard from "../features/dashboard/pages/FinancialDashboard";
import FinancialOrderList from "../features/orderList/pages/FinancialOrderList";
import FinancialOrderDetail from "../features/orderDetail/pages/FinancialOrderDetail";
import Transactions from "../features/transactions/pages/Transactions";
import TransactionDetail from "../features/transactionDetail/pages/TransactionDetail";
import PendingCosts from "../features/pendingTransactions/pages/PendingCosts";

export default function FinancialRoutes() {
  return (
    <Routes>
      <Route path="financialDashboard" element={<FinancialDashboard />} />
      <Route path="orders" element={<FinancialOrderList />} />
      <Route path="orders/detail/:id" element={<FinancialOrderDetail />} />
      <Route path="transactions" element={<Transactions />} />
      <Route path="transactions/:id" element={<TransactionDetail />} />
      <Route path="approvals" element={<PendingCosts />} />
      
      <Route path="*" element={<Navigate to="financialDashboard" replace />} />
    </Routes>
  );
}