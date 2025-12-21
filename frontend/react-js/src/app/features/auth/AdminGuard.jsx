import { useEffect } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAdminAuth } from '../hooks/useAdminAuth';

const AdminGuard = () => {
  const { isAdmin, isLoading, isAuthenticated, isError } = useAdminAuth();
  const location = useLocation();

  // 🔄 لاجیک رفرش خودکار (همونی که خواستی)
  useEffect(() => {
    // اگر ارور داریم (احتمالا ۴۰۱) یا ادمین نیستیم (چون دیتا لود نشد)
    if (isError || (!isLoading && isAuthenticated && !isAdmin)) {
      
      // چک می‌کنیم که قبلاً تو این ۳ ثانیه رفرش نکرده باشیم که لوپ نشه
      const lastRefresh = sessionStorage.getItem('last_force_refresh');
      const now = Date.now();

      if (!lastRefresh || (now - lastRefresh > 5000)) {
        console.log('🔄 Token expired or glitches detected. Force Refreshing...');
        sessionStorage.setItem('last_force_refresh', now);
        window.location.reload();
      }
    }
  }, [isError, isLoading, isAuthenticated, isAdmin]);

  // ۱. لودینگ
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-base-200">
        <span className="loading loading-spinner loading-lg text-primary"></span>
      </div>
    );
  }

  // ۲. احراز هویت
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // ۳. نمایش نرمال (چون اگه مشکلی باشه کد بالا رفرش میکنه)
  return <Outlet />;
};

export default AdminGuard;