import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useNavigate, useLocation } from "react-router-dom";
import { Loader2, Command, ArrowRight, Check, AlertCircle } from "lucide-react";
import { toast } from "sonner";

import useAuthStore from "../../../store/authStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

// --- اسکیمای جدید (بدون محدودیت طول پسورد) ---
const loginSchema = z.object({
  username: z.string().min(1, "لطفاً نام کاربری را وارد کنید"),
  // رمز عبور فقط خالی نباشد، طولش مهم نیست
  password: z.string().min(1, "لطفاً رمز عبور را وارد کنید"),
});

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const login = useAuthStore((state) => state.login);
  const [isLoading, setIsLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const from = location.state?.from?.pathname || "/orders";

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    // شبیه‌سازی یک تاخیر کوتاه برای حس بهتر UX (اختیاری)
    await new Promise((resolve) => setTimeout(resolve, 600));
    
    const success = await login(data.username, data.password);
    setIsLoading(false);

    if (success) {
      toast.success("خوش‌آمدید", {
        description: "شما با موفقیت وارد سیستم شدید.",
        icon: <Check className="text-green-500" />,
      });
      navigate(from, { replace: true });
    } else {
      toast.error("خطای ورود", {
        description: "نام کاربری یا رمز عبور اشتباه است.",
        icon: <AlertCircle className="text-red-500" />,
      });
    }
  };

  return (
    <div className="flex h-screen w-full flex-row overflow-hidden bg-white" dir="rtl">
      {/* === بخش راست: فرم ورود === */}
      <div className="flex w-full flex-col justify-center bg-white px-8 py-12 sm:px-12 lg:w-1/2 xl:px-24 z-10 relative">
        
        {/* هدر موبایل (فقط در سایز کوچک دیده می‌شود) */}
        <div className="mb-8 flex items-center gap-2 lg:hidden">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Command className="h-5 w-5" />
            </div>
            <span className="text-lg font-bold text-gray-900">Printoo Admin</span>
        </div>

        <div className="mx-auto w-full max-w-sm space-y-8 animate-in slide-in-from-right-8 duration-500">
          <div className="space-y-2 text-right">
            <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
              ورود به حساب کاربری
            </h1>
            <p className="text-sm text-gray-500">
              اطلاعات ورود خود را برای دسترسی به داشبورد وارد کنید
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            
            {/* فیلد نام کاربری */}
            <div className="space-y-2">
              <Label htmlFor="username" className="text-gray-700 font-medium">نام کاربری</Label>
              <Input
                id="username"
                placeholder="نام کاربری..."
                disabled={isLoading}
                dir="ltr"
                className="h-12 border-gray-300 bg-gray-50/50 text-lg transition-all focus:border-primary focus:bg-white focus:ring-4 focus:ring-primary/10 placeholder:text-gray-400 text-left"
                {...register("username")}
              />
              {errors.username && (
                <p className="text-xs font-medium text-red-500 animate-pulse">
                  {errors.username.message}
                </p>
              )}
            </div>

            {/* فیلد رمز عبور */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password" className="text-gray-700 font-medium">رمز عبور</Label>
                <a href="#" className="text-xs font-medium text-primary hover:underline hover:text-primary/80 transition-colors">
                  رمز عبور را فراموش کردید؟
                </a>
              </div>
              <Input
                id="password"
                type="password"
                placeholder="••••••"
                disabled={isLoading}
                dir="ltr"
                className="h-12 border-gray-300 bg-gray-50/50 text-lg tracking-widest transition-all focus:border-primary focus:bg-white focus:ring-4 focus:ring-primary/10 placeholder:text-gray-400 text-left"
                {...register("password")}
              />
              {errors.password && (
                <p className="text-xs font-medium text-red-500 animate-pulse">
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* چک‌باکس مرا به خاطر بسپار */}
            <div className="flex items-center space-x-2 space-x-reverse">
              <input
                type="checkbox"
                id="remember"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <label htmlFor="remember" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-600 cursor-pointer select-none">
                مرا به خاطر بسپار
              </label>
            </div>

            {/* دکمه ورود */}
            <Button 
              type="submit" 
              disabled={isLoading} 
              className="group h-12 w-full text-base font-bold shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all duration-300"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin text-white" />
                  <span className="text-white">در حال پردازش...</span>
                </>
              ) : (
                <div className="flex items-center justify-center gap-2 w-full text-white">
                  <span>ورود به سیستم</span>
                  <ArrowRight className="h-5 w-5 transition-transform group-hover:-translate-x-1" />
                </div>
              )}
            </Button>
          </form>

          {/* فوتر فرم */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-gray-400 font-mono">
                PRINTOO MANAGEMENT SYSTEM
              </span>
            </div>
          </div>
          
           <p className="text-center text-xs text-gray-400 mt-6">
            نسخه <span className="font-mono text-gray-600">v1.0.0</span> | تمامی حقوق محفوظ است.
          </p>
        </div>
      </div>

      {/* === بخش چپ: بنر گرافیکی (فقط در دسکتاپ) === */}
      <div className="relative hidden w-0 flex-1 lg:block bg-gray-900">
        {/* پس‌زمینه گرادینت و پترن */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-black z-0"></div>
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#ffffff33_1px,transparent_1px)] [background-size:16px_16px]"></div>
        
        {/* دایره‌های تزیینی */}
        <div className="absolute -top-24 -left-24 h-96 w-96 rounded-full bg-primary/20 blur-3xl filter opacity-40 animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blue-500/10 blur-3xl filter opacity-30"></div>

        {/* محتوای روی بنر */}
        <div className="relative z-10 flex h-full flex-col justify-between p-12 text-white">
          
          {/* لوگوی بالا */}
          <div className="flex items-center gap-3">
             <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/90 text-primary-foreground backdrop-blur-sm shadow-xl">
               <Command className="h-6 w-6" />
             </div>
             <div className="text-xl font-bold tracking-widest uppercase opacity-90">Printoo</div>
          </div>

          {/* متن وسط */}
          <div className="space-y-6 max-w-lg">
            <h2 className="text-4xl font-black leading-tight tracking-tight lg:text-5xl">
              مدیریت هوشمند <br />
              <span className="text-primary">سفارشات چاپ</span>
            </h2>
            <p className="text-lg text-gray-300 leading-relaxed text-justify">
              سیستم جامع مدیریت فرآیندهای چاپ، از ثبت سفارش و طراحی تا لجستیک و حسابداری. دقیق، سریع و یکپارچه.
            </p>
          </div>

          {/* نقل قول یا فوتر پایین */}
          <div className="space-y-2 border-r-2 border-primary pr-4 opacity-80 hover:opacity-100 transition-opacity">
            <blockquote className="text-sm italic text-gray-300">
              "کیفیت، تنها زمانی اتفاق می‌افتد که به جزئیات توجه کنید."
            </blockquote>
            <cite className="block text-xs font-semibold not-italic text-primary">
              تیم فنی پرینتو
            </cite>
          </div>
        </div>
      </div>
    </div>
  );
}