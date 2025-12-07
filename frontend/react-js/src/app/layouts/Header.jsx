// src/app/components/layout/Header.jsx
import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { 
  Menu, 
  Bell, 
  User, 
  LayoutGrid, 
  Search, 
  ChevronDown,
  Wallet,
  ShoppingCart
} from 'lucide-react';
import MegaMenu from '../components/layout/MegaMenu';

const Header = ({ onOpenDrawer }) => {
  const [isMegaMenuOpen, setIsMegaMenuOpen] = useState(false);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const closeTimeoutRef = useRef(null);

  // مدیریت هوشمند hover برای مگامنو
  const handleMouseEnter = () => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current);
    }
    setIsMegaMenuOpen(true);
  };

  const handleMouseLeave = () => {
    closeTimeoutRef.current = setTimeout(() => {
      setIsMegaMenuOpen(false);
    }, 100);
  };

  const handleCreditClick = () => {
    window.open('https://wa.me/9647700000000?text=درخواست شارژ حساب دارم', '_blank');
  };

  return (
    <header className="sticky top-0 z-40 bg-white/85 backdrop-blur-2xl shadow-lg">
      
      {/* هدر اصلی */}
      <div className="container mx-auto px-4 relative">
        
        {/* ردیف اصلی */}
        <div className="h-14 py-3 flex items-center justify-between gap-3">
          
          {/* بخش راست: لوگو و منو موبایل */}
          <div className="flex items-center gap-3">
            
            {/* دکمه منو موبایل */}
            <button 
              onClick={onOpenDrawer} 
              className="lg:hidden btn btn-circle btn-ghost hover:bg-primary/10 hover:text-primary transition-all"
              aria-label="باز کردن منو"
            >
              <Menu size={26} strokeWidth={2.5} />
            </button>

            {/* لوگو */}
            <Link 
              to="/" 
              className="flex items-center group"
            >
              <span className="text-2xl md:text-3xl font-black text-neutral">24</span>
              <a href='/' className="text-2xl md:text-3xl font-black bg-gradient-to-l from-primary to-secondary bg-clip-text text-transparent transition-transform">
                Printoo
              </a>
            </Link>
          </div>

          {/* بخش وسط: جستجو */}
          <div className="flex-1 max-w-xl hidden md:block">
            <div className={`
              relative flex items-center rounded-full border-2 transition-all duration-300
              ${isSearchFocused 
                ? 'border-primary shadow-lg shadow-primary/20 bg-white' 
                : 'border-base-300 bg-base-100 hover:border-primary/50'
              }
            `}>
              <input 
                className="w-full py-2 px-5 pr-12 bg-transparent rounded-full text-right focus:outline-none placeholder:text-base-content/40" 
                placeholder="چی میخوای چاپ کنی؟ اینجا بنویس..."
                onFocus={() => setIsSearchFocused(true)}
                onBlur={() => setIsSearchFocused(false)}
              />
              <button className="absolute right-1 p-2 rounded-full bg-primary text-white hover:bg-primary-focus transition-colors cursor-pointer">
                <Search size={18} />
              </button>
            </div>
          </div>

          {/* بخش چپ: ابزارها */}
          <div className="flex items-center gap-2">
            


            {/* کیف پول / اعتبار */}
            <div 
              onClick={handleCreditClick}
              className="tooltip tooltip-bottom cursor-pointer"
              data-tip="شارژ کیف پول"
            >
              <div className="hidden sm:flex items-center gap-2 bg-gradient-to-l from-emerald-500 to-teal-500 text-white px-2 py-1 rounded-xl hover:shadow-lg hover:shadow-emerald-500/30 transition-all hover:scale-[1.02] active:scale-95">
                <Wallet size={20} />
                <div className="flex flex-col items-start leading-tight">
                  <span className="text-[10px] opacity-80">موجودی</span>
                  <span className="font-bold text-sm dir-ltr">250,000 IQD</span>
                </div>
              </div>
            </div>

            {/* سبد خرید */}
            <div className="tooltip tooltip-bottom" data-tip="سبد خرید">
              <button className="btn btn-circle btn-ghost hover:bg-primary/10 hover:text-primary relative">
                <ShoppingCart size={22} />
                <span className="absolute -top-1 -right-1 min-w-5 h-5 flex items-center justify-center text-xs font-bold bg-error text-white rounded-full">
                  ۳
                </span>
              </button>
            </div>

            {/* اطلاعیه‌ها */}
            <div className="tooltip tooltip-bottom" data-tip="پیام‌ها و اطلاعیه‌ها">
              <button className="btn btn-circle btn-ghost hover:bg-primary/10 hover:text-primary relative">
                <Bell size={22} />
                <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-error rounded-full animate-pulse"></span>
              </button>
            </div>

            {/* پروفایل کاربر */}
            <div className="dropdown dropdown-end">
              <div 
                tabIndex={0} 
                role="button" 
                className="tooltip tooltip-bottom btn btn-circle btn-ghost hover:bg-primary/10 border-2 border-base-300 hover:border-primary transition-colors"
                data-tip="حساب کاربری"
              >
                <User size={22} />
              </div>
              <ul tabIndex={0} className="dropdown-content z-[100] menu p-2 shadow-xl bg-white rounded-2xl w-56 mt-3 border border-base-200">
                <li>
                  <Link to="/profile" className="flex items-center gap-3 py-3 hover:bg-primary/10 rounded-xl">
                    <User size={18} />
                    حساب کاربری
                  </Link>
                </li>
                <li>
                  <Link to="/orders" className="flex items-center gap-3 py-3 hover:bg-primary/10 rounded-xl">
                    <ShoppingCart size={18} />
                    سفارش‌های من
                  </Link>
                </li>
                <div className="divider my-1"></div>
                <li>
                  <button className="flex items-center gap-3 py-3 text-error hover:bg-error/10 rounded-xl">
                    خروج از حساب
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* نوار دسته‌بندی - فقط دسکتاپ */}
        <div className="hidden lg:block border-t border-base-200">
          <div className="flex items-center gap-1 py-2">
            
            {/* دکمه دسته‌بندی با مگامنو */}
            <div className="relative">
              <button 
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
                className={`
                  flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold transition-all
                  ${isMegaMenuOpen 
                    ? 'bg-primary text-white shadow-lg shadow-primary/30' 
                    : 'bg-base-200 hover:bg-primary hover:text-white text-base-content'
                  }
                `}
              >
                <LayoutGrid size={20} />
                <span>همه دسته‌ها</span>
                <ChevronDown 
                  size={16} 
                  className={`transition-transform duration-300 ${isMegaMenuOpen ? 'rotate-180' : ''}`}
                />
              </button>
            </div>

            {/* لینک‌های سریع */}
            <div className="flex items-center gap-1 mr-2">
              {[
                { label: '🔥 پرفروش‌ها', to: '/bestsellers' },
                { label: '💎 جدیدترین‌ها', to: '/new' },
                { label: '🎁 تخفیف‌ها', to: '/offers' },
                { label: '📦 پیگیری سفارش', to: '/tracking' },
              ].map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  className="px-4 py-2 text-sm font-medium text-base-content/70 hover:text-primary hover:bg-primary/5 rounded-lg transition-all"
                >
                  {item.label}
                </Link>
              ))}
            </div>

            {/* شماره تماس پشتیبانی */}
            <div className="mr-auto flex items-center gap-2 text-sm text-base-content/60">
              <span>📞</span>
              <span className="font-bold dir-ltr">0770-000-0000</span>
              <span className="text-xs">(پشتیبانی ۲۴ ساعته)</span>
            </div>
          </div>
        </div>

        {/* مگامنو */}
        <div 
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          className={`
            absolute top-full right-0 left-0
            transition-all durationorigin-top ease-out z-50
            ${isMegaMenuOpen ? 'opacity-100 visible translate-y-0' : 'opacity-0 invisible -translate-y-2 pointer-events-none'}
          `}
        >
          <MegaMenu isOpen={isMegaMenuOpen} />
        </div>

      </div>
    </header>
  );
};

export default Header;
