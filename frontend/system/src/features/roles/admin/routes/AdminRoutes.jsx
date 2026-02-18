import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import AdminDashboard from "../features/dashboard/pages/AdminDashboard";
import AdminOrderList from "../features/orderList/pages/AdminOrderList";
import CreateOrder from "../features/orderDetail/pages/CreateOrder";
import OrderDetail from "../features/orderDetail/pages/OrderDetail";
import StaffList from "../features/users/pages/StaffList";
import CustomerList from "../features/customers/pages/CustomerList";
import CreateCustomer from "../features/customers/pages/CreateCustomer";
import CustomerDetail from "../features/customers/pages/CustomerDetail";
<Route path="customers/:id" element={<CustomerDetail />} />


export default function AdminRoutes() {
  return (
    <Routes>
      {/* مسیرها باید نسبت به ریشه ادمین باشن (بدون اسلش اول) */}
      <Route path="adminDashboard" element={<AdminDashboard />} />
      <Route path="orders" element={<AdminOrderList />} />
      <Route path="orders/new" element={<CreateOrder />} />
      <Route path="orders/:id" element={<OrderDetail />} />
      <Route path="users/staff" element={<StaffList />} />
      <Route path="customers" element={<CustomerList />} />
      <Route path="customers/create" element={<CreateCustomer />} />
      <Route path="customers/:id" element={<CustomerDetail />} />
      
      {/* اگر هیچ کدوم نبود، بره به داشبورد ادمین */}
      <Route path="/" element={<Navigate to="adminDashboard" replace />} />
    </Routes>
  );
}