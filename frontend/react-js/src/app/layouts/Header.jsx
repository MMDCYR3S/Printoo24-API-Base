import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { cartService } from '../services/cartService';
import { 
  Menu, 
  Bell, 
  User, 
  LayoutGrid, 
  Search, 
  ChevronDown,
  Wallet,
  ShoppingCart,
  X
} from 'lucide-react';
import MegaMenu from '../components/layout/MegaMenu';
import pageText from '../lang/pages.json'
import globalText from '../lang/global.json'

// ایمپورت‌های مربوط به کیف پول و فرمت‌کننده
import { useWalletBalance } from '../hooks/useWalletBalance';
import { formatCurrency } from '../utils/formatters';

// ایمپورت‌های جدید برای سیستم جستجو (ماژولار)
import { useSearch } from '../hooks/useSearch';
import SearchOverlay from './SearchOverlay';

const Header = ({ onOpenDrawer }) => {
  const [isMegaMenuOpen, setIsMegaMenuOpen] = useState(false);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [cartCount, setCartCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState(''); // استیت متن جستجو
  const closeTimeoutRef = useRef(null);

  // استفاده از هوک جستجو برای مدیریت منطق و اسکرول بی‌نهایت
  const { results, loading, hasMore, loadMore } = useSearch(searchQuery);

  // دریافت تعداد آیتم‌های سبد خرید
  useEffect(() => {
    const fetchCartCount = async () => {
      if (isLoggedIn) {
        try {
          const count = await cartService.getTotalNumber();
          setCartCount(count || 0);
        } catch (error) {
          console.error("خطا در دریافت تعداد سبد خرید:", error);
        }
      }
    };
    fetchCartCount();
  }, [isLoggedIn]);

  // بررسی وضعیت لاگین
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    setIsLoggedIn(!!token);
  }, []);

  // استفاده از هوک اختصاصی کیف پول (موجود در کد شما)
  const { balance, loading: walletLoading } = useWalletBalance(isLoggedIn);

  // مدیریت باز و بسته شدن مگامنو
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
    window.open('https://wa.me/9647700000000', '_blank');
  };

  return (
    <header className="sticky top-0 z-40 bg-white/85 backdrop-blur-2xl shadow-lg">
      <div className="container mx-auto px-4 relative">
        <div className="h-14 py-3 flex items-center justify-between gap-3">
          
          {/* بخش لوگو و منوی موبایل */}
          <div className="flex items-center gap-3">
            <button 
              onClick={onOpenDrawer} 
              className="lg:hidden btn btn-circle btn-ghost hover:bg-primary/10 hover:text-primary transition-all"
              aria-label={pageText.layout.Header.openMenu}
            >
              <Menu size={26} strokeWidth={2.5} />
            </button>

            <Link to="/" className="flex items-center group">
              <span className="text-2xl md:text-3xl font-black text-neutral">24</span>
              <span className="text-2xl md:text-3xl font-black bg-gradient-to-l from-primary to-secondary bg-clip-text text-transparent transition-transform">
                Printoo
              </span>
            </Link>
          </div>

          {/* بخش جستجوی دسکتاپ (تغییر یافته برای جستجوی هوشمند) */}
          <div className="flex-1 max-w-xl hidden md:block relative group">
            <div className={`
              relative flex items-center rounded-full border-2 transition-all duration-300
              ${isSearchFocused 
                ? 'border-primary shadow-lg shadow-primary/20 bg-white' 
                : 'border-base-300 bg-base-100 hover:border-primary/50'
              }
            `}>
              <input 
                className="w-full py-2 px-5 pr-24 bg-transparent rounded-full text-right focus:outline-none placeholder:text-base-content/40" 
                placeholder={pageText.layout.Header.search}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setIsSearchFocused(true)}
                // تایم‌اوت برای اینکه کلیک روی نتایج جستجو قبل از بسته شدن انجام شود
onBlur={() => setTimeout(() => setIsSearchFocused(false), 300)}
              />
              <div className="absolute right-1 flex items-center gap-1">
                {searchQuery && (
                  <button 
                    onClick={() => setSearchQuery('')}
                    className="p-1 hover:bg-base-200 rounded-full transition-colors text-base-content/40"
                  >
                    <X size={14} />
                  </button>
                )}
                <button className="p-2 rounded-full bg-primary text-white hover:bg-primary-focus transition-colors cursor-pointer">
                  <Search size={18} />
                </button>
              </div>
            </div>

            {/* کامپوننت ماژولار نمایش نتایج */}
            <SearchOverlay 
              isVisible={isSearchFocused && searchQuery.length >= 2}
              results={results}
              loading={loading}
              hasMore={hasMore}
              onLoadMore={loadMore}
              onClose={() => setIsSearchFocused(false)}
            />
          </div>

          {/* بخش ابزارها (سبد خرید، کیف پول، حساب کاربری) */}
          <div className="flex items-center gap-2">
            
            <div className="tooltip tooltip-bottom" data-tip={globalText.cart}>
              <Link to="/cart" className="btn btn-circle btn-ghost hover:bg-primary/10 hover:text-primary relative">
                <ShoppingCart size={22} />
                {cartCount > 0 && (
                  <span className="absolute -top-1 -right-1 min-w-5 h-5 flex items-center justify-center text-xs font-bold bg-error text-white rounded-full">
                    {cartCount}
                  </span>
                )}
              </Link>
            </div>

            {isLoggedIn ? (
              <>
                {/* بخش کیف پول */}
                <div 
                  onClick={handleCreditClick}
                  className="tooltip tooltip-bottom cursor-pointer"
                  data-tip={pageText.layout.ManinLayout.AccountCharge}
                >
                  <div className="hidden sm:flex items-center gap-2 bg-gradient-to-l from-emerald-500 to-teal-500 text-white px-2 py-1 rounded-xl hover:shadow-lg hover:shadow-emerald-500/30 transition-all hover:scale-[1.02] active:scale-95">
                    <Wallet size={20} />
                    <div className="flex flex-col items-start leading-tight">
                      <span className="text-[10px] opacity-80">{pageText.layout.Header.amout}</span>
                      {walletLoading ? (
                        <div className="h-4 w-16 bg-white/40 animate-pulse rounded mt-0.5"></div>
                      ) : (
                        <span className="font-bold text-sm dir-ltr">
                          {formatCurrency(balance)} IQD
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* بخش حساب کاربری */}
                <div className="dropdown dropdown-end">
                  <div 
                    tabIndex={0} 
                    role="button" 
                    className="tooltip tooltip-bottom btn btn-circle btn-ghost hover:bg-primary/10 border-2 border-base-300 hover:border-primary transition-colors"
                    data-tip={pageText.layout.Header.account}
                  >
                    <User size={22} />
                  </div>
                  <ul tabIndex={0} className="dropdown-content z-[100] menu p-2 shadow-xl bg-white rounded-2xl w-56 mt-3 border border-base-200">
                    <li>
                      <Link to="/profile" className="flex items-center gap-3 py-3 hover:bg-primary/10 rounded-xl">
                        <User size={18} />
                        {pageText.layout.Header.account}
                      </Link>
                    </li>
                    <li>
                      <Link to="/profile/orders" className="flex items-center gap-3 py-3 hover:bg-primary/10 rounded-xl">
                        <ShoppingCart size={18} />
                        {pageText.layout.Header.myOrders}
                      </Link>
                    </li>
                    <div className="divider my-1"></div>
                    <li>
                      <button className="flex items-center gap-3 py-3 text-error hover:bg-error/10 rounded-xl">
                        {pageText.layout.Header.logout}
                      </button>
                    </li>
                  </ul>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-1 sm:gap-2 mr-1">
                <Link 
                  to="/login" 
                  className="btn btn-ghost btn-sm sm:btn-md hover:bg-primary/10 hover:text-primary rounded-xl font-bold transition-colors"
                >
                  {globalText.header.login}
                </Link>
                <Link 
                  to="/register" 
                  className="btn btn-primary btn-sm sm:btn-md rounded-xl text-white font-bold shadow-lg shadow-primary/30 hover:shadow-primary/50 hover:-translate-y-0.5 transition-all"
                >
                  {globalText.header.register}
                </Link>
              </div>
            )}
            
          </div>
        </div>

        {/* نوار دسته‌بندی و لینک‌های سریع */}
        <div className="hidden lg:block border-t border-base-200">
          <div className="flex items-center gap-1 py-2">
            
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
                <span>{pageText.layout.Header.allCategories}</span>
                <ChevronDown 
                  size={16} 
                  className={`transition-transform duration-300 ${isMegaMenuOpen ? 'rotate-180' : ''}`}
                />
              </button>
            </div>

            <div className="flex items-center gap-1 mr-2">
              {[
                { label: pageText.layout.Header.allProducts , to: '/shop' },
                { label: pageText.layout.Header.lastOrders , to: '/profile/orders' },
                { label: pageText.layout.Header.myAddresses  , to: '/profile/addresses' },
                { label: pageText.layout.Header.trackingOrder , to: 'https://wa.me/9647700000000' },
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

            <div className="mr-auto flex items-center gap-2 text-sm text-base-content/60">
              <span>📞</span>
              <span className="font-bold dir-ltr">0770-000-0000</span>
              <span className="text-xs">
                {pageText.layout.Header.contactUs}
              </span>
            </div>
          </div>
        </div>

        {/* مگامنو با انیمیشن و وضعیت هوشمند */}
        <div 
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          className={`
            absolute top-full right-0 left-0
            transition-all duration-300 ease-out z-50
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