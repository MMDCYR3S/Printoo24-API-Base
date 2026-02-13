import React from "react";
import { NavLink } from "react-router-dom"; 
import { cn } from "@/lib/utils";
import { ChevronLeft } from "lucide-react";

// ورودی‌ها را تغییر دادم تا وضعیت را از لی‌اوت بگیرد (برای کش آمدن صفحه)
export default function Sidebar({ items = [], collapsed, onToggle }) {
  
  return (
    <aside
      className={cn(
        "relative flex flex-col border-l border-gray-light bg-gray-dark text-gray-light shadow-xl transition-all duration-300 ease-in-out z-40 h-[calc(100vh-4rem)] fixed right-0 top-16 hidden md:flex",
        collapsed ? "w-16" : "w-56" 
      )}
    >
      {/* دکمه Toggle */}
      <button
        onClick={onToggle}
        className="absolute -left-3 top-6 z-50 flex h-6 w-6 items-center justify-center rounded-full border border-gray-600 bg-gray-dark text-gold-light hover:bg-gray-700 hover:text-white shadow-md transition-transform focus:outline-none"
      >
        <ChevronLeft
          className={cn(
            "h-4 w-4 transition-transform duration-300",
            collapsed && "rotate-180"
          )}
        />
      </button>

      {/* منو */}
      <nav className="flex-1 space-y-3 p-3 mt-4 overflow-y-auto custom-scrollbar" dir="rtl">
        {items.map((item, index) => {
           const Icon = item.icon;
           return (
            <NavLink
              key={index}
              to={item.href}
              title={collapsed ? item.title : ""}
              className={({ isActive }) =>
                cn(
                  "group flex cursor-pointer items-center rounded-md p-3 font-medium transition-all duration-200 border-[1px] shadow-md shadow-black/70",
                  
                  // استایل پیش فرض
                  "border-gold-light/40 text-gold-light hover:border-gold-dark hover:text-white hover:bg-gold-dark/10",
                  
                  // استایل اکتیو (دقیقاً کد شما)
                  isActive 
                    ? "inset-shadow-sm inset-shadow-black text-gold-light border-gold-light font-bold shadow-gray-dark hover:text-gold-light hover:bg-gray-dark hover:border-gold-light" 
                    : "bg-transparent",
                    
                  collapsed ? "justify-center" : "justify-start gap-3"
                )
              }
            >
              {/* آیکون */}
              <Icon
                className={cn(
                  "shrink-0 transition-colors h-5 w-5",
                  // هندل کردن رنگ آیکون در حالت اکتیو (دقیقاً کد شما)
                  "text-gold-light group-hover:text-white", 
                  "[.active_&]:text-gray-900 group-hover:text-gold-light"
                )}
              />

              {/* متن */}
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
        })}
      </nav>
      
      {/* فوتر */}
      {!collapsed && (
        <div className="p-4 text-center border-t border-gray-700/50 mt-auto">
          <div className="text-xs text-gray-500 opacity-50 font-mono">v1.0.0 Beta</div>
        </div>
      )}
    </aside>
  );
}