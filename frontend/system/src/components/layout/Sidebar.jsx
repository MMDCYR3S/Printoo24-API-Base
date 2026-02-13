import React from "react";
import { NavLink } from "react-router-dom"; 
import { cn } from "@/lib/utils";
import { ChevronLeft } from "lucide-react";

export default function Sidebar({ items = [], collapsed, onToggle }) {
  
  // تابع کمکی برای رندر کردن یک آیتم منو
  const renderNavItem = (item, index) => {
    const Icon = item.icon;
    return (
      <NavLink
        key={index}
        to={item.href}
        title={collapsed ? item.title : ""}
        className={({ isActive }) =>
          cn(
            "group flex cursor-pointer items-center rounded-md p-3 transition-all duration-200  mb-2  shadow-md shadow-black/50",
            
            // --- استایل پیش‌فرض (Inactive) ---
            " hover:text-gold-light !bg-white/5",
            
            // --- استایل اکتیو (امضای دیزاین شما) ---
            isActive 
              ? "inset-shadow-sm inset-shadow-black hover:border-gold-light-70 text-gold-light border border-r-gold-light border-l-gold-light border-t-gold-dark/90 border-b-gold-dark/90 !bg-gray-dark shadow-none" 
              : "bg-transparent",
              
            collapsed ? "justify-center px-0" : "justify-start gap-3"
          )
        }
      >
        <Icon
          className={cn(
            "shrink-0 transition-all duration-300",
            collapsed ? "h-6 w-6" : "h-5 w-5",
            // رنگ آیکون در حالت‌های مختلف
            "[.active_&]:text-gold-light group-hover:text-gold-light"
          )}
        />

        <span
          className={cn(
            "overflow-hidden whitespace-nowrap transition-all duration-300",
            collapsed ? "w-0 opacity-0 hidden" : "w-auto opacity-100"
          )}
        >
          {item.title}
        </span>
      </NavLink>
    );
  };

  return (
    <aside
      className={cn(
        "relative flex flex-col border-l border-gray-700 bg-gray-dark text-gray-light shadow-2xl transition-all duration-300 ease-in-out z-40 h-[calc(100vh-4rem)] fixed right-0 top-16 hidden md:flex",
        collapsed ? "w-19" : "w-56" 
      )}
    >
      {/* دکمه Toggle: چسبیده به لبه (Jira Style) */}
      <button
        onClick={onToggle}
        className="absolute top-6 -left-3 z-50 flex h-6 w-6 items-center justify-center rounded-full border border-gray-600 bg-gray-800 text-gold-light hover:bg-gold-light hover:text-gray-900 shadow-lg transition-all focus:outline-none group"
      >
        <ChevronLeft
          className={cn(
            "h-3 w-3 transition-transform duration-300",
            collapsed ? "rotate-180" : "rotate-0"
          )}
        />
      </button>

      {/* کانتینر اسکرول‌دار منو */}
      <nav className="flex-1 overflow-y-auto custom-scrollbar py-4 px-3" dir="rtl">
        
        {/* بررسی می‌کنیم دیتای ورودی فلت است یا گروه‌بندی شده */}
        {items.map((sectionOrItem, idx) => {
          
          // حالت ۱: اگر آیتم گروپ شده است (مثل ادمین)
          if (sectionOrItem.items) {
            return (
              <div key={sectionOrItem.id || idx}>
                
                {/* جداکننده (Divider) بین گروه‌ها */}
                {idx > 0 && (
                  <div className={cn(
                    "my-4 border-t border-dashed border-gray-700/50 mx-2",
                    collapsed && "mx-1 my-2"
                  )} />
                )}

                {/* تایتل گروه (فقط وقتی باز است) */}
                {!collapsed && (
                  <h3 className="mb-2 px-2 text-[10px] font-bold uppercase tracking-wider text-gray-500">
                    {sectionOrItem.title}
                  </h3>
                )}

                {/* رندر آیتم‌های داخل گروه */}
                {sectionOrItem.items.map((subItem, subIdx) => renderNavItem(subItem, `g-${idx}-${subIdx}`))}
              </div>
            );
          }

          // حالت ۲: اگر لیست فلت است (برای سایر نقش‌ها)
          return renderNavItem(sectionOrItem, idx);
        })}

      </nav>
      
      {/* فوتر ورژن */}
      <div className={cn(
        "p-4 border-t border-gray-800 bg-black/20 transition-all",
        collapsed ? "text-center" : "flex justify-between items-center"
      )}>
        {!collapsed ? (
            <>
                <span className="text-[10px] text-gray-500">Printoo System</span>
                <span className="text-[10px] font-mono text-gold-dark">v1.0.0</span>
            </>
        ) : (
            <span className="text-[9px] font-mono text-gold-dark">v1</span>
        )}
      </div>
    </aside>
  );
}