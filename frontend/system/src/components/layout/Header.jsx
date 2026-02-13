import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { LogOut, User, ChevronDown, Mail, Shield, Fingerprint, Tag } from "lucide-react";
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
      
      {/* --- سمت راست: لوگو و اکشن‌ها --- */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-9 border-l border-gray-600">
          <div className="text-lg font-bold text-gold-light tracking-wider">
            Printoo<span className="text-white">Admin</span>
          </div>
        </div>

        <div className="hidden md:flex items-center gap-3">
          {actions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Link key={index} to={action.href}>
                <Button 
                  size="sm"
                  className="h-9 px-4 gap-2 font-bold shadow-md shadow-black/60 cursor-pointer text-gold-light border border-gold-dark/60 bg-gray-dark hover:shadow-gold-dark/30 hover:bg-gray-dark"
                >
                  <Icon className="h-4 w-4" />
                  {action.title}
                </Button>
              </Link>
            )
          })}
        </div>
      </div>

      {/* --- سمت چپ: تاریخ و دراپ‌داون کامل اطلاعات --- */}
      <div className="flex items-center gap-4">
        
        <div className="hidden md:flex items-center justify-center h-9 px-4 rounded-md bg-gray-dark border border-gold-dark/60 text-gold-light font-bold text-sm shadow-md shadow-black/60 outline-none">
           {formattedDate} / {formattedTime}
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-2 h-[2.25rem] shadow-md shadow-black/60 cursor-pointer px-3 rounded-md bg-gray-dark border border-gold-dark/60 outline-none">
               <div className="h-6 w-6 rounded-full bg-gray-800 flex items-center justify-center text-gold-light">
                 <User className="h-4 w-4" />
               </div>
               <span className="text-sm font-bold text-gold-light truncate max-w-[80px]">
                 {user?.full_name || "پروفایل"}
               </span>
               <ChevronDown className="h-4 w-4 text-gold-dark" />
            </button>
          </DropdownMenuTrigger>
          
          <DropdownMenuContent className="w-72 bg-gray-dark border-gold-dark/40 text-gray-100" align="start">
            <DropdownMenuLabel className="text-right text-gold-light border-b mx-2 border-gold-dark/60 pb-2 mb-2">
               اطلاعات کاربری
            </DropdownMenuLabel>
            
            {/* نمایش تمام فیلدهای موجود در دیتای یوزر طبق خروجی API شما */}
            <div className="px-2 py-1 space-y-1 text-gold-dark">
              <ProfileItem icon={<User size={18}/>} label="نام کامل" value={user?.full_name} />
              <ProfileItem icon={<Fingerprint size={18}/>} label="نام کاربری" value={user?.username} />
              <ProfileItem icon={<Mail size={18}/>} label="ایمیل" value={user?.email} />
              <ProfileItem icon={<Shield size={18}/>} label="نقش سیستمی" value={user?.role} />
              <ProfileItem icon={<Tag size={18}/>} label="عنوان نقش" value={user?.role_name} />
              <ProfileItem icon={<span className="text-[16px] font-medium">ID</span>} label="شناسه کاربر" value={user?.id} />
            </div>

            <DropdownMenuSeparator className="bg-gold-dark/60 mx-2" />
            
            <DropdownMenuItem 
              onClick={logout} 
              className="text-red-500 focus:bg-red-500/10 focus:text-red-500 cursor-pointer justify-between flex-row-reverse font-bold"
            >
              <LogOut className="h-4 w-4" />
              <span>خروج از حساب</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

      </div>
    </header>
  );
}

// کامپوننت داخلی برای نمایش ردیف‌های اطلاعات
function ProfileItem({ icon, label, value }) {
  return (
    <div className="flex items-center justify-between text-[11px] p-2 rounded hover:bg-white/5 transition-colors border-b border-white/5 last:border-0">
      <span className="text-gray-light text-xs">{value || "---"}</span>
      <div className="flex items-center gap-2 text-gold-light/80">
        <span className="text-gold-light text-xs">{label}</span>
        {icon}
      </div>
    </div>
  );
}