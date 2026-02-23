import { useState, useRef, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
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
  X,
  LogOut,
  Package,
  MapPin,
  Phone,
  Headphones,
  Store,
} from 'lucide-react';
import MegaMenu from '../components/layout/MegaMenu';
import pageText from '../lang/pages.json';
import globalText from '../lang/global.json';

import { useWalletBalance } from '../hooks/useWalletBalance';
import { formatCurrency } from '../utils/formatters';

import { useSearch } from '../hooks/useSearch';
import SearchOverlay from './SearchOverlay';

import { useNavigate } from 'react-router-dom';
/* ─────────────────────────────────────────────
   Header — نوار بالای صفحه
   ───────────────────────────────────────────── */
const Header = ({ onOpenDrawer }) => {
  const [isMegaMenuOpen, setIsMegaMenuOpen] = useState(false);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [cartCount, setCartCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const closeTimeoutRef = useRef(null);
  const searchInputRef = useRef(null);

  const { results, loading, hasMore, loadMore } = useSearch(searchQuery);


const navigate = useNavigate();

  // 1. تعریف تابع خروج
  const handleLogout = () => {
    // پاک کردن توکن از لوکال استوریج
    localStorage.removeItem('accessToken') 
    localStorage.removeItem('guest_token') 
    localStorage.removeItem('refreshToken') 
    localStorage.removeItem('userData') 
    localStorage.removeItem('userId') 
    
    // هدایت کاربر به صفحه لاگین
    // refresh page
    window.location.reload();
    navigate('/');
  };



  // دریافت تعداد سبد خرید
  useEffect(() => {
    const fetchCartCount = async () => {
      if (isLoggedIn) {
        try {
          const count = await cartService.getTotalNumber();
          setCartCount(count || 0);
        } catch (error) {
          console.error('خطا در دریافت تعداد سبد خرید:', error);
        }
      }
    };
    fetchCartCount();
  }, [isLoggedIn]);

  // بررسی لاگین
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    setIsLoggedIn(!!token);
  }, []);

  const { balance, loading: walletLoading } = useWalletBalance(isLoggedIn);

  // مگامنو
  const handleMouseEnter = useCallback(() => {
    if (closeTimeoutRef.current) clearTimeout(closeTimeoutRef.current);
    setIsMegaMenuOpen(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    closeTimeoutRef.current = setTimeout(() => setIsMegaMenuOpen(false), 120);
  }, []);

  const handleCreditClick = () => {
    window.open('https://wa.me/9647762278666', '_blank');
  };

  // بستن جستجو با Escape
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        setIsSearchFocused(false);
        searchInputRef.current?.blur();
      }
    };
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, []);

  return (
    <header className="sticky top-0 z-40 bg-radial from-white to-slate-200 backdrop-blur-2xl border-b border-slate-200 shadow-[0_1px_12px_-2px_rgba(0,0,0,0.08)]">
      <div className="container mx-auto px-4 relative">

        {/* ════════════════ ردیف اصلی ════════════════ */}
        <div className="h-16 flex items-center justify-between gap-4">

          {/* ── لوگو + منوی موبایل ── */}
          <div className="flex items-center gap-2.5">
            <button
              onClick={onOpenDrawer}
              className="
                lg:hidden w-10 h-10 flex items-center justify-center
                rounded-xl text-slate-600
                hover:bg-primary/10 hover:text-primary
                active:scale-95 transition-all duration-200
              "
              aria-label={pageText.layout.Header.openMenu}
            >
              <Menu size={22} strokeWidth={2.2} />
            </button>

            <Link to="/" className="flex items-center group gap-0.5">
              <span className="text-[26px] md:text-3xl font-black text-slate-800 tracking-tighter transition-colors group-hover:text-slate-900">
                
              </span>
              <span className="text-[26px] md:text-3xl font-black bg-radial from-primary drop-shadow-primary/50 drop-shadow-lg to-secondary bg-clip-text text-transparent">
                Printoo24
              </span>
            </Link>
          </div>

          {/* ── جستجوی دسکتاپ ── */}
          <div className="flex-1 max-w-xl hidden md:block relative">
            <div
              className={`
                relative flex items-center rounded-2xl transition-all duration-300
                ${isSearchFocused
                  ? 'bg-white ring-2 ring-primary/30 shadow-lg shadow-primary/10'
                  : 'bg-slate-100/80 ring-1 ring-slate-200 hover:ring-slate-300 hover:bg-slate-100'
                }
              `}
            >
              <input
                ref={searchInputRef}
                className="
                  w-full py-2.5 px-5 pr-24 bg-transparent rounded-2xl
                  text-right text-sm text-slate-700
                  focus:outline-none
                  placeholder:text-slate-400/70 placeholder:text-sm
                "
                placeholder={pageText.layout.Header.search}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setIsSearchFocused(true)}
                onBlur={() => setTimeout(() => setIsSearchFocused(false), 300)}
              />
              <div className="absolute right-1.5 flex items-center gap-1">
                <AnimatePresence>
                  {searchQuery && (
                    <motion.button
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      onClick={() => {
                        setSearchQuery('');
                        searchInputRef.current?.focus();
                      }}
                      className="p-1.5 hover:bg-slate-200/80 rounded-full transition-colors text-slate-400"
                    >
                      <X size={13} />
                    </motion.button>
                  )}
                </AnimatePresence>
                <button
                  className="
                    p-2 rounded-xl bg-radial from-primary drop-shadow-primary/50 drop-shadow-lg to-secondary text-white
                    active:scale-95
                    transition-all duration-200 cursor-pointer
                  "
                >
                  <Search size={16} strokeWidth={2.5} />
                </button>
              </div>
            </div>

            {/* نتایج جستجو */}
            <SearchOverlay
              isVisible={isSearchFocused && searchQuery.length >= 2}
              results={results}
              loading={loading}
              hasMore={hasMore}
              onLoadMore={loadMore}
              onClose={() => setIsSearchFocused(false)}
            />
          </div>

          {/* ── ابزارها (سبد خرید، کیف پول، حساب) ── */}
          <div className="flex items-center gap-1.5 sm:gap-2">

            {/* سبد خرید */}
            <div className="tooltip tooltip-bottom" data-tip={globalText.cart}>
              <Link
                to="/cart"
                className="
                  relative w-10 h-10 flex items-center justify-center
                  rounded-xl text-slate-600
                  hover:bg-primary/10 hover:text-primary
                  active:scale-95 transition-all duration-200 ring ring-slate-200
                "
              >
                <ShoppingCart size={21} strokeWidth={1.8} />
                <AnimatePresence>
                  {cartCount > 0 && (
                    <motion.span
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      exit={{ scale: 0 }}
                      className="
                        absolute -top-0.5 -right-0.5
                        min-w-[20px] h-5 flex items-center justify-center
                        text-[10px] font-bold
                        bg-red-500 text-white rounded-full
                        shadow-sm shadow-red-500/30
                        px-1
                      "
                    >
                      {cartCount}
                    </motion.span>
                  )}
                </AnimatePresence>
              </Link>
            </div>

            {isLoggedIn ? (
              <>
                {/* کیف پول */}
                <div
                  onClick={handleCreditClick}
                  className="tooltip tooltip-bottom cursor-pointer"
                  data-tip={pageText.layout.ManinLayout.AccountCharge}
                >
                  <div className="
                    hidden sm:flex items-center gap-2.5
                    bg-radial from-primary to-secondary
                    text-white px-3 py-2 rounded-xl
                    hover:shadow-lg hover:shadow-emerald-500/25
                    hover:scale-[1.02] active:scale-[0.98]
                    transition-all duration-200
                  ">
                    <div className="w-8 h-8 rounded-lg bg-white/15 backdrop-blur-sm flex items-center justify-center">
                      <Wallet size={17} />
                    </div>
                    <div className="flex flex-col items-start leading-tight">
                      <span className="text-[10px] text-white/70 font-medium">
                        {pageText.layout.Header.amout}
                      </span>
                      {walletLoading ? (
                        <div className="h-4 w-16 bg-white/25 animate-pulse rounded mt-0.5" />
                      ) : (
                        <span className="font-bold text-[13px] dir-ltr tracking-tight">
                          {formatCurrency(balance)} IQD
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* حساب کاربری */}
                <div className="dropdown dropdown-end">
                  <div
                    tabIndex={0}
                    role="button"
                    className="
                      tooltip tooltip-bottom
                      w-10 h-10 flex items-center justify-center
                      rounded-xl text-slate-600
                      ring-1 ring-slate-200
                      hover:bg-primary/10 hover:text-primary hover:ring-primary/30
                      active:scale-95 transition-all duration-200
                    "
                    data-tip={pageText.layout.Header.account}
                  >
                    <User size={20} strokeWidth={1.8} />
                  </div>
                  <ul
                    tabIndex={0}
                    className="
                      dropdown-content z-[100] menu p-1.5
                      bg-white/[0.98] backdrop-blur-xl
                      shadow-[0_12px_40px_-8px_rgba(0,0,0,0.12)]
                      rounded-2xl w-56 mt-3
                      ring-1 ring-black/[0.05]
                    "
                  >
                    <li>
                      <Link
                        to="/profile"
                        className="flex items-center gap-3 py-2.5 px-3 text-sm font-medium text-slate-700 hover:bg-primary/10 hover:text-primary rounded-xl transition-colors"
                      >
                        <User size={17} strokeWidth={1.8} />
                        {pageText.layout.Header.account}
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/profile/orders"
                        className="flex items-center gap-3 py-2.5 px-3 text-sm font-medium text-slate-700 hover:bg-primary/8 hover:text-primary rounded-xl transition-colors"
                      >
                        <Package size={17} strokeWidth={1.8} />
                        {pageText.layout.Header.myOrders}
                      </Link>
                    </li>
                    <div className="my-1 mx-3 border-t border-slate-200" />
                    <li>
                      <button onClick={handleLogout}  className="flex items-center gap-3 py-2.5 px-3 text-sm font-medium text-red-500 hover:bg-red-50 rounded-xl transition-colors w-full">
                        <LogOut size={17} strokeWidth={1.8} />
                        {pageText.layout.Header.logout}
                      </button>
                    </li>
                  </ul>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-1.5 sm:gap-2 mr-1">
                <Link
                  to="/login"
                  className="
                    px-4 py-2 text-sm font-bold
                    text-slate-600 hover:text-primary
                    hover:bg-primary/8
                    rounded-xl transition-all duration-200
                  "
                >
                  {globalText.header.login}
                </Link>
                <Link
                  to="/register"
                  className="
                    px-4 py-2 text-sm font-bold
                    bg-primary text-white rounded-xl
                    shadow-md shadow-primary/25
                    hover:shadow-lg hover:shadow-primary/35
                    hover:-translate-y-[1px]
                    active:translate-y-0 active:shadow-md
                    transition-all duration-200
                  "
                >
                  {globalText.header.register}
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* ════════════════ نوار دسته‌بندی (دسکتاپ) ════════════════ */}
        <div className="hidden lg:block border-t border-slate-100">
          <div className="flex items-center gap-1 py-1.5">

            {/* دکمه مگامنو */}
            <div className="relative">
              <button
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold
                  transition-all duration-250 ease-out
                  ${isMegaMenuOpen
                    ? 'bg-primary text-white shadow-md shadow-primary/25'
                    : 'bg-slate-100/80 text-slate-700 hover:bg-primary hover:text-white hover:shadow-md hover:shadow-primary/20'
                  }
                `}
              >
                <LayoutGrid size={18} strokeWidth={2} />
                <span>{pageText.layout.Header.allCategories}</span>
                <ChevronDown
                  size={14}
                  className={`transition-transform duration-300 ${isMegaMenuOpen ? 'rotate-180' : ''}`}
                />
              </button>
            </div>

            {/* لینک‌های سریع */}
            <nav className="flex items-center gap-0.5 mr-1">
              {[
                { label: pageText.layout.Header.allProducts, to: '/shop', icon: Store },
                { label: pageText.layout.Header.lastOrders, to: '/profile/orders', icon: Package },
                { label: pageText.layout.Header.myAddresses, to: '/profile/addresses', icon: MapPin },
                { label: pageText.layout.Header.trackingOrder, to: 'https://wa.me/9647762278666', icon: Headphones },
              ].map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  className="
                    px-3 py-1.5 text-[13px] font-medium
                    text-slate-500 hover:text-primary
                    hover:bg-primary/5
                    rounded-lg transition-all duration-200
                    flex items-center gap-1.5
                  "
                >
                { <item.icon  size={20} /> }
                  {item.label}
                </Link>
              ))}
            </nav>

            {/* شماره تماس */}
            <div className="mr-auto flex items-center gap-2 text-sm text-slate-400">
              <div className="flex items-center gap-1.5 bg-slate-50 px-3 py-1.5 rounded-lg">
                <Phone size={13} strokeWidth={2} className="text-slate-400" />
                <span className="font-bold text-slate-500 dir-ltr text-xs tracking-wide">
                  0770-6227-8666
                </span>
              </div>
              <span className="text-[11px] text-slate-400 hidden xl:inline">
                {pageText.layout.Header.contactUs}
              </span>
            </div>
          </div>
        </div>

        {/* ════════════════ مگامنو ════════════════ */}
        <div
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          className={`
            absolute top-full right-0 left-0 z-50
            transition-all duration-300 ease-out
            ${isMegaMenuOpen
              ? 'opacity-100 visible translate-y-0'
              : 'opacity-0 invisible -translate-y-2 pointer-events-none'
            }
          `}
        >
          <MegaMenu isOpen={isMegaMenuOpen} onClose={() => setIsMegaMenuOpen(false)} />
        </div>

      </div>
    </header>
  );
};

export default Header;