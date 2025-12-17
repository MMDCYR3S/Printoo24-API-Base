// src/app/features/admin/layouts/SidebarItem.jsx
import { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft } from 'lucide-react';

const SidebarItem = ({ item }) => {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  
  // بررسی می‌کنیم آیا کاربر الان داخل یکی از زیرمجموعه‌های این منو هست؟
  const isActiveParent = item.children?.some(child => location.pathname.startsWith(child.path));

  // اگر والد فعال بود، همیشه موقع لود باز باشه
  useEffect(() => {
    if (isActiveParent) setIsOpen(true);
  }, [isActiveParent]);

  const Icon = item.icon;

  // ۱. اگر آیتم فرزند نداشت (لینک ساده) - بدون تغییر
  if (!item.children) {
    return (
      <NavLink
        to={item.path}
        end={item.path === '/admin'}
        className={({ isActive }) => `
          flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 font-medium text-sm
          ${isActive 
            ? 'bg-primary text-white shadow-lg shadow-primary/30' 
            : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'
          }
        `}
      >
        {Icon && <Icon size={20} />}
        <span>{item.title}</span>
      </NavLink>
    );
  }

  // ۲. اگر آیتم پدر بود (دارای زیرمنو)
  return (
    <div 
      className="flex flex-col gap-1"
      // ✨ اضافه شدن قابلیت باز شدن با هاور
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => {
        // فقط اگر منو فعال نبود، موقع رفتن موس بسته شود
        // این باعث میشه وقتی تو زیرمنوها هستی، منو نپره
        if (!isActiveParent) setIsOpen(false);
      }}
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          flex items-center justify-between w-full px-4 py-3 rounded-xl transition-all duration-200 font-bold text-sm select-none
          ${isActiveParent ? 'text-primary bg-primary/5' : 'text-slate-600 hover:bg-slate-100'}
        `}
      >
        <div className="flex items-center gap-3">
          {Icon && <Icon size={20} />}
          <span>{item.title}</span>
        </div>
        
        {/* آیکون فلش با انیمیشن چرخش */}
        <motion.div
          animate={{ rotate: isOpen ? -90 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronLeft size={16} />
        </motion.div>
      </button>

      {/* انیمیشن باز و بسته شدن لیست فرزندان */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }} // انیمیشن نرم و سریع
            className="overflow-hidden"
          >
            <div className="flex flex-col gap-1 pr-4 border-r-2 border-slate-100 mr-5 my-1">
              {item.children.map((child) => (
                <NavLink
                  key={child.path}
                  to={child.path}
                  className={({ isActive }) => `
                    flex items-center gap-2 px-3 py-2.5 rounded-lg transition-all text-xs font-medium relative overflow-hidden
                    ${isActive 
                      ? 'text-primary bg-primary/10 translate-x-1 font-bold' 
                      : 'text-slate-400 hover:text-slate-700 hover:bg-slate-50'
                    }
                  `}
                >
                   {/* نشانگر اکتیو بودن */}
                   <span className={`w-1.5 h-1.5 rounded-full transition-colors ${location.pathname === child.path ? 'bg-primary' : 'bg-slate-300'}`}></span>
                   {child.title}
                </NavLink>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SidebarItem;