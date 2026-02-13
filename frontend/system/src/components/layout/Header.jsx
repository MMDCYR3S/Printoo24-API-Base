import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { LogOut, User, ChevronDown, Command } from "lucide-react";
import useAuthStore from "@/store/authStore";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function Header({ actions = [] }) {
  const { user, logout } = useAuthStore();
  const [dateTime, setDateTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setDateTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  const formattedDate = new Intl.DateTimeFormat("fa-IR", {
    month: "long",
    day: "numeric",
  }).format(dateTime);

  const formattedTime = new Intl.DateTimeFormat("fa-IR", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(dateTime);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex h-16 items-center justify-between bg-gray-dark px-4 shadow-md transition-all border-b border-gray-700" dir="rtl">
      
      {/* --- سمت راست: لوگو و دکمه‌های اکشن (طبق تصویر) --- */}
      <div className="flex items-center gap-4">
        
        {/* لوگو */}
        <div className="flex items-center gap-2  px-9 border-l border-gray-600">
          <div className="text-lg font-bold text-gold-light tracking-wider">
            Printoo<span className="text-white">Admin</span>
          </div>
        </div>

        {/* دکمه‌های اکشن (افزودن سفارش / افزودن مشتری) */}
        <div className="hidden md:flex items-center gap-3">
          {actions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Link key={index} to={action.href}>
                <Button 
                  size="sm"
                  className={cn(
                    "h-9 px-4 gap-2 font-bold shadow-sm transition-all",
                    // استایل طبق تصویر: طوسی روشن با بوردر طلایی
                    " text-gold-light border border-gold-dark/60 bg-gray-dark shadow-md shadow-black/60 cursor-pointer hover:shadow-gold-dark/30 hover:bg-gray-dark "
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {action.title}
                </Button>
              </Link>
            )
          })}
        </div>
      </div>

      {/* --- سمت چپ: تاریخ و پروفایل --- */}
      <div className="flex items-center gap-4 ">
        
        {/* تاریخ و ساعت (باکس طوسی طبق تصویر) */}
        <div className="hidden md:flex items-center justify-center h-9 px-4 rounded-md bg-gray-dark border border-gold-dark/60 text-gold-light font-bold text-sm shadow-md shadow-black/60 outline-none">
           {formattedDate} / {formattedTime}
        </div>

        {/* منوی پروفایل (باکس طوسی طبق تصویر) */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex  items-center gap-2 h-[2.25rem] shadow-md shadow-black/60 cursor-pointer px-3 rounded-md bg-gray-dark border border-gold-dark/60 ">
               <div className="h-6 w-6 rounded-full bg-gray-800 flex items-center justify-center text-gold-light">
                 <User className="h-4 w-4" />
               </div>
               <span className="text-sm font-bold text-gold-light truncate max-w-[80px]">
                 {user?.first_name || "نام پروفایل"}
               </span>
               <ChevronDown className="h-4 w-4 text-gold-dark" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end">
            <DropdownMenuLabel>حساب کاربری</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout} className="text-red-600 cursor-pointer">
              <LogOut className="ml-2 h-4 w-4" />
              <span>خروج</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

      </div>
    </header>
  );
}