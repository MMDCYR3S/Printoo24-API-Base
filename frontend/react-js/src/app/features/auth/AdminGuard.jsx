// src/app/features/auth/AdminGuard.jsx
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAdminAuth } from '../hooks/useAdminAuth';

const AdminGuard = () => {
  // ✅ قدم اول: همیشه هوک‌ها را در بالاترین خط صدا بزنید
  // حتی اگر توکن نداریم، این هوک باید اجرا شود (خودش هندل می‌کند)
  const { isAdmin, isLoading, isAuthenticated } = useAdminAuth();
  
  const location = useLocation();

  // ✅ قدم دوم: حالا شرط‌ها و returnها را بنویسید
  
  // ۱. حالت لودینگ
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-base-200">
        <span className="loading loading-spinner loading-lg text-primary"></span>
      </div>
    );
  }

  // ۲. اگر احراز هویت نشده (توکن ندارد یا توکن نامعتبر است)
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // ۳. اگر ادمین نیست
  if (!isAdmin) {
    return (
      <div className="p-10 text-center">
        <h1 className="text-3xl font-bold text-error">دسترسی غیرمجاز ⛔</h1>
        <p className="mt-4">شما مجوز ورود به این بخش را ندارید.</p>
        <a href="/" className="btn btn-primary mt-6">بازگشت به خانه</a>
      </div>
    );
  }

  // ۴. همه چیز اوکی است
  return <Outlet />;
};

export default AdminGuard;