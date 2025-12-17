// src/app/features/admin/layouts/AdminLayout.jsx
import { Outlet, Link } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import { authService } from '../../../services/authService';
import SidebarItem from './SidebarItem';
import AdminHeader from './AdminHeader';
import { ADMIN_NAVIGATION } from '../constants/navigation';

const AdminLayout = () => {
  const handleLogout = () => {
     authService.logout();
     window.location.href = '/login';
  };

  return (
    <div className="drawer lg:drawer-open font-sans bg-slate-50 min-h-screen">
      <input id="admin-drawer" type="checkbox" className="drawer-toggle" />
      
      {/* === محتوای اصلی === */}
      <div className="drawer-content flex flex-col transition-all duration-300">
        <AdminHeader />
        
        <main className="flex-1 p-6 md:p-8 overflow-y-auto">
          {/* اینجا محتوای صفحات ادمین رندر میشه */}
          <Outlet />
        </main>
      </div> 
      
      {/* === سایدبار === */}
      <div className="drawer-side z-50 shadow-2xl lg:shadow-none">
        <label htmlFor="admin-drawer" className="drawer-overlay bg-black/20 backdrop-blur-sm"></label> 
        
        <aside className="w-72 min-h-full bg-white text-base-content flex flex-col border-l border-base-200">
          {/* هدر سایدبار */}
          <div className="h-16 flex items-center gap-2 px-6 border-b border-base-100">
            <span className="text-2xl font-black text-slate-800">Printoo</span>
            <span className="badge badge-primary badge-outline text-xs font-bold">Admin Panel</span>
          </div>

          {/* لیست منوها */}
          <div className="flex-1 overflow-y-auto custom-scrollbar py-4 px-3 space-y-1">
             {ADMIN_NAVIGATION.map((item, index) => (
                <SidebarItem key={index} item={item} />
             ))}
          </div>

          {/* فوتر سایدبار */}
          <div className="p-4 border-t border-base-100 bg-slate-50">
            <button 
              onClick={handleLogout}
              className="btn btn-outline btn-error w-full btn-sm gap-2 hover:shadow-error/20"
            >
              <LogOut size={16} />
              خروج امن
            </button>
            <div className="text-center text-[10px] text-slate-300 mt-3 font-mono">
              v2.0.0 Pro Edition
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default AdminLayout;