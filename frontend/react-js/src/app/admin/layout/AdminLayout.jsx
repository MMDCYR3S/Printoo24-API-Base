import { Outlet, Link, useLocation } from "react-router-dom";
import { LayoutDashboard, Users, Box, LogOut } from "lucide-react";

const AdminLayout = () => {
  const location = useLocation();

  const menuItems = [
    { title: "داشبورد", icon: <LayoutDashboard size={20} />, path: "/admin" },
    { title: "محصولات", icon: <Box size={20} />, path: "/admin/products" },
    { title: "کاربران", icon: <Users size={20} />, path: "/admin/users" },
  ];

  return (
    <div className="drawer lg:drawer-open font-sans bg-base-200 min-h-screen">
      <input id="admin-drawer" type="checkbox" className="drawer-toggle" />
      
      {/* محتوای اصلی صفحه */}
      <div className="drawer-content flex flex-col">
        {/* هدر موبایل */}
        <div className="w-full navbar bg-base-100 lg:hidden shadow-sm">
          <div className="flex-none">
            <label htmlFor="admin-drawer" aria-label="open sidebar" className="btn btn-square btn-ghost">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="inline-block w-6 h-6 stroke-current"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </label>
          </div>
          <div className="flex-1 px-2 mx-2 font-bold text-primary">پنل مدیریت</div>
        </div>

        {/* محل رندر شدن صفحات داخلی ادمین */}
        <main className="p-6">
            <Outlet />
        </main>
      </div> 
      
      {/* سایدبار */}
      <div className="drawer-side z-50">
        <label htmlFor="admin-drawer" aria-label="close sidebar" className="drawer-overlay"></label> 
        <ul className="menu p-4 w-80 min-h-full bg-base-100 text-base-content border-l border-base-300">
          {/* لوگو یا تایتل */}
          <li className="mb-6">
             <div className="text-2xl font-bold text-primary px-2">Admin Panel</div>
          </li>

          {/* آیتم‌های منو */}
          {menuItems.map((item) => (
            <li key={item.path} className="mb-1">
              <Link 
                to={item.path} 
                className={location.pathname === item.path ? "active font-bold" : ""}
              >
                {item.icon}
                {item.title}
              </Link>
            </li>
          ))}

          <div className="divider"></div>
          
          <li>
            <button className="text-error hover:bg-error/10">
              <LogOut size={20} />
              خروج
            </button>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default AdminLayout;