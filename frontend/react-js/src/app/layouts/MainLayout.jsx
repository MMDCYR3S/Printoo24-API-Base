// src/app/features/layout/MainLayout.jsx
import { useState, useCallback, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Layers, Headphones } from 'lucide-react';

import Header from './Header';
import Footer from './Footer';
import MobileMenu from '../components/layout/MobileMenu';
import SupportFloat from '../components/common/SupportFloat';
import pageText from '../lang/pages.json';

const MainLayout = () => {

  const { pathname } = useLocation();

  // useEffect برای اسکرول به بالا هنگام تغییر مسیر
  useEffect(() => {
    window.scrollTo(0, 0); // پرهش به بالای صفحه
  }, [pathname]); // این افکت فقط وقتی pathname عوض شه اجرا میشه

  const [isDrawerOpen, setDrawerOpen] = useState(false);


  const openDrawer = useCallback(() => setDrawerOpen(true), []);
  const closeDrawer = useCallback(() => setDrawerOpen(false), []);

  return (
    <div className="relative min-h-screen flex flex-col bg-white">

      {/* ── هدر ── */}
      <Header onOpenDrawer={openDrawer} />

      {/* ── محتوای اصلی ── */}
      <main className="flex-1 mx-auto py-6 w-full">
        <Outlet />
      </main>

      {/* ── فوتر ── */}
      <Footer />

      {/* ── دکمه پشتیبانی ── */}
      <SupportFloat />

      {/* ════════════════ دراور موبایل ════════════════ */}
      <AnimatePresence>
        {isDrawerOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">

            {/* اورلی */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
              className="absolute inset-0 bg-black/40 backdrop-blur-[2px]"
              onClick={closeDrawer}
            />

            {/* پنل سایدبار */}
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', stiffness: 320, damping: 30 }}
              className="
                absolute inset-y-0 right-0 w-[300px]
                bg-white
                shadow-[−24px_0_48px_−12px_rgba(0,0,0,0.15)]
                flex flex-col
                overflow-hidden
              "
            >
              {/* ── هدر سایدبار ── */}
              <div className="
                shrink-0 px-5 py-4
                flex items-center justify-between
                border-b border-slate-100
                bg-gradient-to-l from-primary/5 to-transparent
              ">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 flex items-center justify-center">
                    <Layers size={17} className="text-primary" />
                  </div>
                  <span className="text-base font-extrabold text-slate-800">
                  دابەشکردنی بەرهەمەکان
                  </span>
                </div>
                <button
                  onClick={closeDrawer}
                  className="
                    w-8 h-8 flex items-center justify-center
                    rounded-lg
                    text-slate-400 hover:text-red-500
                    hover:bg-red-50
                    active:scale-95
                    transition-all duration-200
                  "
                >
                  <X size={18} strokeWidth={2.2} />
                </button>
              </div>

              {/* ── محتوای منو ── */}
              <div className="flex-1 overflow-y-auto custom-scrollbar">
                <MobileMenu onClose={closeDrawer} />
              </div>

              {/* ── فوتر سایدبار ── */}
              <div className="shrink-0 border-t border-slate-100 bg-slate-50/50 p-4 space-y-3">
                <a href="https://wa.me/9647762278666" target="_blank" rel="noreferrer" title="WhatsApp" className="
                  w-full flex items-center justify-center gap-2
                  py-2.5 rounded-xl
                  bg-gradient-to-l from-secondary to-secondary/90
                  text-white text-sm font-bold
                  shadow-md shadow-secondary/20
                  hover:shadow-lg hover:shadow-secondary/30
                  active:scale-[0.98]
                  transition-all duration-200
                ">
                  <Headphones size={16} />
                  {pageText.layout.MainLaouy}
                </a>

              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MainLayout;