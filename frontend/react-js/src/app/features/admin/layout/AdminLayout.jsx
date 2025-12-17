// src/app/features/admin/layouts/AdminLayout.jsx
import { Outlet } from 'react-router-dom';
import { LogOut, Menu } from 'lucide-react';
import { authService } from '../../../services/authService';
import SidebarItem from './SidebarItem';
import AdminHeader from './AdminHeader';
import { ADMIN_NAVIGATION } from '../constants/navigation';

const AdminLayout = () => {
  const handleLogout = () => {
     authService.logout();
     window.location.href = '/login';
  };

  // محتوای سایدبار (چون دو جا استفاده میشه، کامپوننت یا متغیرش می‌کنیم که کد تکراری نشه)
  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-white text-base-content border-l border-base-200 min-h-screen">
      {/* هدر سایدبار */}
      <div className="h-16 flex items-center gap-2 px-6 border-b border-base-100 shrink-0">
        <span className="text-2xl font-black text-slate-800">Printoo</span>
        <span className="badge badge-primary badge-outline text-xs font-bold">Admin</span>
      </div>

      {/* لیست منوها */}
      <div className="flex-1 overflow-y-auto custom-scrollbar py-4 px-3 space-y-1">
         {ADMIN_NAVIGATION.map((item, index) => (
            <SidebarItem key={index} item={item} />
         ))}
      </div>

      {/* فوتر سایدبار */}
      <div className="p-4 border-t border-base-100 bg-slate-50 shrink-0">
        <button 
          onClick={handleLogout}
          className="btn btn-outline btn-error w-full btn-sm gap-2 hover:shadow-error/20"
        >
          <LogOut size={16} />
          خروج
        </button>
      </div>
    </div>
  );

  return (
    // کانتینر اصلی: ارتفاع کل صفحه، جلوگیری از اسکرول بادی
    <div className="flex h-screen w-full bg-slate-50 overflow-hidden font-sans">
      
      {/* 🖥️ بخش ۱: سایدبار دسکتاپ (فقط در lg و بالاتر دیده میشه) */}
      {/* این یک div ساده است، پس هیچ لایه‌ای روی بقیه نمیندازه */}
      <aside className="hidden lg:block w-72 h-full shadow-xl z-30">
        <SidebarContent />
      </aside>


      {/* 📱 بخش ۲: دراور موبایل (فقط در زیر lg فعال میشه) */}
      <div className="drawer lg:hidden absolute inset-0 pointer-events-none z-50">
        <input id="admin-drawer" type="checkbox" className="drawer-toggle" />
        
        {/* کانتنت دراور (خالیه چون کانتنت اصلی رو جدا گذاشتیم، این فقط برای باز شدن منو هست) */}
        <div className="drawer-content">
            {/* دکمه‌ای اینجا نیست چون تو هدر گذاشتیم */}
        </div> 
        
        <div className="drawer-side pointer-events-auto">
          <label htmlFor="admin-drawer" className="drawer-overlay bg-black/40 backdrop-blur-sm"></label>
          <div className="w-72 min-h-full">
            <SidebarContent />
          </div>
        </div>
      </div>


      {/* 📄 بخش ۳: محتوای اصلی صفحه (Content Area) */}
      <div className="flex-1 flex flex-col h-full min-w-0 overflow-hidden relative">
        
        {/* هدر */}
        <AdminHeader />
        
        {/* اسکرول فقط توی این ناحیه انجام میشه */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth">
          <Outlet />
        </main>
      </div>

    </div>
  );
};

export default AdminLayout;