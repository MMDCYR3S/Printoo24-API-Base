import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import useAuthStore from "../../store/authStore";

const ProtectedRoute = ({ children }) => {
  // دریافت وضعیت احراز هویت از استور سراسری
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  // دریافت مکان فعلی کاربر (مثلاً /orders)
  const location = useLocation();

  if (!isAuthenticated) {
    // ریدارکت به لاگین، همراه با ذخیره آدرس فعلی در state
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // اگر لاگین بود، کامپوننت فرزند (مثلاً DashboardLayout) را رندر کن
  return children;
};

export default ProtectedRoute;