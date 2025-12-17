// src/app/features/admin/layouts/AdminHeader.jsx
import { Menu, Bell, Search } from 'lucide-react';
import { useAdminAuth } from '../../hooks/useAdminAuth';

const AdminHeader = () => {
  const { user } = useAdminAuth();

  return (
    <header className="navbar bg-white/80 backdrop-blur-md sticky top-0 z-20 border-b border-base-200 px-6 h-16">
      <div className="flex-1 flex flex-row gap-4">
        {/* دکمه منو موبایل */}
        <label htmlFor="admin-drawer" className="btn btn-square btn-ghost lg:hidden text-slate-500">
          <Menu size={24} />
        </label>
        
        {/* سرچ بار مینیمال */}
        <div className="hidden md:flex items-center gap-2 bg-slate-100 px-4 py-2 rounded-full w-full max-w-sm transition-all focus-within:bg-white focus-within:ring-2 ring-primary/20">
            <Search size={18} className="text-slate-400"/>
            <input type="text" placeholder="جستجو در پنل..." className="bg-transparent text-sm w-full outline-none placeholder:text-slate-400"/>
        </div>
      </div>

      <div className="flex-none flex flex-row gap-4">
        {/* نوتیفیکیشن */}
        <button className="btn btn-circle btn-ghost btn-sm text-slate-500 relative">
          <Bell size={20} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-error rounded-full animate-pulse"></span>
        </button>

        {/* پروفایل ادمین */}
        <div className="flex items-center gap-3 pl-2 border-l-2 border-slate-100">
            <div className="text-left hidden md:block">
                <div className="text-sm font-bold text-slate-800">{user?.first_name || 'Admin'}</div>
                <div className="text-[10px] text-slate-400 font-mono">Super Admin</div>
            </div>
            <div className="avatar placeholder">
              <div className="bg-primary text-white rounded-full w-9 h-9 shadow-lg shadow-primary/30">
                <span className="text-sm font-bold">{user?.username?.[0]?.toUpperCase()}</span>
              </div>
            </div>
        </div>
      </div>
    </header>
  );
};

export default AdminHeader;