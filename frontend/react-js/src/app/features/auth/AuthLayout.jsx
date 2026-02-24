import { Outlet } from 'react-router-dom';

const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-base-200 flex items-center justify-center p-4">
      <div className="card w-full max-w-md bg-base-100 shadow-xl">
        <div className="card-body">
          {/* لوگوی پروژه یا تیتر مشترک */}
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold text-primary">Printoo24</h1>
            <p className="text-sm text-base-content/70 mt-2">سامانه مدیریت سفارشات چاپ</p>
          </div>
          
          {/* محتوای متغیر صفحات (Login/Register) اینجا قرار می‌گیرد */}
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;