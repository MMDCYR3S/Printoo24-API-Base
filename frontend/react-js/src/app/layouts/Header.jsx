// src/app/components/layout/Header.jsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, Bell, User, LogOut, LayoutGrid, Search, ChevronDown } from 'lucide-react';
import MegaMenu from '../components/layout/MegaMenu';

const Header = ({ onOpenDrawer }) => {
  const [isMegaMenuOpen, setIsMegaMenuOpen] = useState(false);

  // لینک واتساپ
  const handleCreditClick = () => {
    window.open('https://wa.me/9647700000000?text=درخواست شارژ حساب دارم', '_blank');
  };

  return (
    <header className="sticky top-0 z-40 bg-base-100 shadow-sm border-b border-base-200" onMouseLeave={() => setIsMegaMenuOpen(false)}>
      
      {/* Top Bar */}
      <div className="bg-neutral text-neutral-content px-4 py-1 text-xs md:text-sm font-bold flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="animate-pulse inline-block w-2 h-2 bg-red-600 rounded-full"></span>
          <p>وضعیت مرز: <span className="bg-white/20 px-2 rounded mx-1">۲ ساعت تاخیر</span></p>
        </div>
        <div className="hidden md:block dir-ltr font-mono">1000 IQD = 42,500 T</div>
      </div>

      <div className="container mx-auto px-4 h-20 flex items-center justify-between gap-4 relative">
        
        {/* راست: لوگو و تریگر مگامنو */}
        <div className="flex items-center gap-6 h-full">
          <button onClick={onOpenDrawer} className="lg:hidden btn btn-square btn-ghost tooltip tooltip-bottom" data-tip="منو">
            <Menu size={24} />
          </button>

          <Link to="/" className="text-3xl font-black text-primary tracking-tighter hover:scale-105 transition-transform">
            Printoo<span className="text-neutral">24</span>
          </Link>

          {/* دکمه دسته‌بندی (تریگر) */}
          <div 
            className="hidden lg:flex items-center h-full"
            onMouseEnter={() => setIsMegaMenuOpen(true)}
          >
            <button className={`btn btn-ghost btn-sm text-base-content/80 font-bold gap-2 text-lg px-4 ${isMegaMenuOpen ? 'bg-base-200' : ''}`}>
              <LayoutGrid size={20} />
              دسته‌بندی محصولات
              <ChevronDown size={16} className={`transition-transform duration-300 ${isMegaMenuOpen ? 'rotate-180' : ''}`}/>
            </button>
          </div>
        </div>

        {/* وسط: سرچ باکس بزرگ */}
        <div className="flex-1 max-w-2xl hidden md:block px-8">
          <div className="join w-full shadow-sm hover:shadow-md transition-shadow duration-300">
            <button className="btn btn-neutral join-item px-6 font-bold text-white">
               جستجو
            </button>
            <input 
              className="input input-bordered join-item w-full text-right focus:outline-none bg-base-200/50 focus:bg-white transition-colors placeholder:text-base-content/40" 
              placeholder="نام محصول را بنویسید (مثلاً: تراکت گلاسه)..." 
            />
          </div>
        </div>

        {/* چپ: ابزارها */}
        <div className="flex items-center gap-3">
          
          {/* باکس اعتبار */}
          <div 
            onClick={handleCreditClick}
            className="hidden lg:flex flex-col items-end bg-emerald-50 border border-emerald-200 px-4 py-1.5 rounded-xl cursor-pointer hover:shadow-md transition-all group mr-2 tooltip tooltip-bottom"
            data-tip="برای شارژ کلیک کنید"
          >
            <span className="text-[11px] text-emerald-600 font-bold">اعتبار شما</span>
            <div className="font-black text-xl text-emerald-800 dir-ltr leading-none mt-0.5">
              250,000 <span className="text-xs font-medium">IQD</span>
            </div>
          </div>

          {/* نوتیفیکیشن با تول‌تیپ */}
          <div className="tooltip tooltip-bottom" data-tip="اطلاعیه‌ها">
            <button className="btn btn-circle btn-ghost hover:bg-base-200 transition-colors">
              <div className="indicator">
                <Bell size={22} />
                <span className="badge badge-xs badge-error indicator-item animate-pulse"></span>
              </div>
            </button>
          </div>

          {/* پروفایل */}
          <div className="dropdown dropdown-end tooltip tooltip-left" data-tip="حساب کاربری">
            <div tabIndex={0} role="button" className="btn btn-circle btn-ghost avatar placeholder border border-base-300">
              <div className="bg-neutral text-neutral-content rounded-full w-full">
                <User size={22}/>
              </div>
            </div>
            <ul tabIndex={0} className="mt-3 z-[1] p-2 shadow-lg border border-base-200 menu menu-sm dropdown-content bg-base-100 rounded-box w-52">
              <li className="menu-title text-base-content/50">کاربر عزیز، خوش آمدید</li>
              <li><Link to="/profile" className="py-2">پروفایل و تنظیمات</Link></li>
              <li><Link to="/orders" className="py-2">سفارش‌های من</Link></li>
              <div className="divider my-1"></div>
              <li><button className="text-error font-bold hover:bg-error/10"><LogOut size={16}/> خروج از حساب</button></li>
            </ul>
          </div>
        </div>
      </div>

      {/* مگا منو (خارج از کانتینر محدود کننده) */}
      {/* این بخش حالا تمام عرض صفحه را می‌گیرد چون خارج از div های بالایی است */}
      <div 
        className={`absolute top-full left-0 right-0 bg-base-100 border-t border-base-200 shadow-2xl transition-all duration-300 origin-top ease-out overflow-hidden z-50 ${isMegaMenuOpen ? 'opacity-100 visible translate-y-0' : 'opacity-0 invisible -translate-y-2 pointer-events-none'}`}
        onMouseEnter={() => setIsMegaMenuOpen(true)}
        onMouseLeave={() => setIsMegaMenuOpen(false)}
      >
        <MegaMenu />
      </div>
    </header>
  );
};

export default Header;