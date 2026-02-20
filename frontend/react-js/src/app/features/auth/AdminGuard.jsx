import { Navigate, Outlet } from 'react-router-dom';

const AdminGuard = () => {

  // ۱. خوندن خام دیتا
  const rawData = localStorage.getItem('userData');

  if (!rawData) {
    console.error("2. NO DATA FOUND IN LOCALSTORAGE! Redirecting to login...");
    return <Navigate to="/login" replace />;
  }

  try {
    // ۲. بررسی اینکه آیا دیتا استرینگ هست یا خودش آبجکت شده
    let user;
    if (typeof rawData === 'string') {
      user = JSON.parse(rawData);
    } else {
      user = rawData;
    }

    // ۳. چک کردن فیلدهای حیاتی (دقیقاً بر اساس چیزی که فرستادی)
    const staffStatus = user.is_staff;
    const superuserStatus = user.is_superuser;
    


    // شرط ورود: هر کدوم true باشن (چه بولین چه رشته "true")
    const isAdmin = 
      staffStatus === true || 
      staffStatus === "true" || 
      superuserStatus === true || 
      superuserStatus === "true";


    if (isAdmin) {

      return <Outlet />;
    } else {
      return <Navigate to="/" replace />;
    }

  } catch (err) {

    return <Navigate to="/login" replace />;
  }
};

export default AdminGuard;