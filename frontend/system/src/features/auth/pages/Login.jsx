import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useNavigate, useLocation } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

// ایمپورت از استور و کامپوننت‌های UI
import useAuthStore from "../../../store/authStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

// تعریف اسکیما اعتبارسنجی با Zod
const loginSchema = z.object({
  username: z.string().min(1, "نام کاربری الزامی است"),
  password: z.string().min(1, "رمز عبور الزامی است"),
});

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const login = useAuthStore((state) => state.login); // اکشن لاگین از استور
  const [isLoading, setIsLoading] = useState(false);

  // آدرسی که کاربر می‌خواست برود ولی به اینجا پرت شد (یا پیش‌فرض داشبورد)
  const from = location.state?.from?.pathname || "/";

  // تنظیم هوک فرم
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  // تابع ارسال فرم
  const onSubmit = async (data) => {
    setIsLoading(true);
    
    // فراخوانی متد لاگین از استور
    const success = await login(data.username, data.password);

    if (success) {
      toast.success("ورود موفقیت‌آمیز بود");
      // هدایت به صفحه مقصد (یا داشبورد)
      navigate(from, { replace: true });
    } else {
      toast.error("نام کاربری یا رمز عبور اشتباه است");
    }
    
    setIsLoading(false);
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-100 px-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">ورود به سیستم</CardTitle>
          <CardDescription>
            برای دسترسی به پنل مدیریت پرینتو ۲۴ وارد شوید
          </CardDescription>
        </CardHeader>
        
        <form onSubmit={handleSubmit(onSubmit)}>
          <CardContent className="space-y-4">
            {/* فیلد نام کاربری */}
            <div className="space-y-2">
              <Label htmlFor="username">نام کاربری</Label>
              <Input
                id="username"
                type="text"
                placeholder="admin"
                disabled={isLoading}
                {...register("username")}
                className={errors.username ? "border-red-500" : ""}
              />
              {errors.username && (
                <p className="text-xs text-red-500">{errors.username.message}</p>
              )}
            </div>

            {/* فیلد رمز عبور */}
            <div className="space-y-2">
              <Label htmlFor="password">رمز عبور</Label>
              <Input
                id="password"
                type="password"
                disabled={isLoading}
                {...register("password")}
                className={errors.password ? "border-red-500" : ""}
              />
              {errors.password && (
                <p className="text-xs text-red-500">{errors.password.message}</p>
              )}
            </div>
          </CardContent>

          <CardFooter>
            <Button className="w-full" type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  در حال ورود...
                </>
              ) : (
                "ورود"
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}