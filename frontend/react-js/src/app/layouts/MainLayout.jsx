// src/app/features/layout/MainLayout.jsx
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';
import MobileMenu from '../components/layout/MobileMenu'; // اطمینان از ایمپورت
import { X } from 'lucide-react';

const MainLayout = () => {
  
  // ✅ تعریف تابعی که فراموش شده بود
  const closeDrawer = () => {
    const drawerCheckbox = document.getElementById('main-drawer');
    if (drawerCheckbox) {
      drawerCheckbox.checked = false;
    }
  };

  const openDrawer = () => {
    const drawerCheckbox = document.getElementById('main-drawer');
    if (drawerCheckbox) {
      drawerCheckbox.checked = true;
    }
  };

  return (
    <div className="drawer ">
      <input id="main-drawer" type="checkbox" className="drawer-toggle" />
      
      {/* 🟢 محتوای اصلی صفحه (Page Content) */}
      <div className="drawer-content flex flex-col min-h-screen bg-base-200">
        {/* هدر: تابع باز کردن دراور را به آن پاس می‌دهیم */}
        <Header onOpenDrawer={openDrawer} />
        
        {/* بدنه اصلی صفحات */}
        <main className="flex-1 container mx-auto px-4 py-6">
          <Outlet />
        </main>
        
        <Footer />
      </div>

      {/* 🟠 سایدبار کشویی (Sidebar Content) */}
      <div className="drawer-side z-50 " >
        <label htmlFor="main-drawer" aria-label="close sidebar" className="drawer-overlay"></label>
        
        <div className="menu p-0 w-80 min-h-full bg-base-100 text-base-content flex flex-col shadow-2xl">
          
          {/* هدر سایدبار */}
          <div className="p-4 flex justify-between items-center border-b border-base-200 sticky top-0 bg-base-100 z-10">
            <span className="text-xl font-black text-primary">دسته‌بندی‌ها</span>
            {/* دکمه بستن */}
            <button onClick={closeDrawer} className="btn btn-ghost btn-circle btn-sm hover:bg-error/10 hover:text-error transition-colors">
                <X size={24} />
            </button>
          </div>

          {/* محتوای منوی موبایل (که قبلاً ساختیم) */}
          <div className="flex-1 overflow-y-auto custom-scrollbar">
             {/* تابع بستن را به کامپوننت پاس می‌دهیم تا وقتی روی لینک کلیک شد، منو بسته شود */}
             <MobileMenu onClose={closeDrawer} />
          </div>
          
          {/* فوتر سایدبار */}
          <div className="p-4 border-t border-base-200 mt-auto bg-base-50">
             <button className="btn btn-secondary w-full mb-3 shadow-md font-bold text-lg">
                شارژ سریع حساب
             </button>
             <div className="text-center text-xs text-base-content/40 font-mono" dir="ltr">
               Printoo24 v1.0.0
             </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default MainLayout;