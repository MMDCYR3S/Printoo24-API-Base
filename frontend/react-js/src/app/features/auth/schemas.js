import { z } from 'zod';

// اسکیما برای فرم ورود
export const loginSchema = z.object({
  username: z.string().min(1, 'نام کاربری الزامی است'),
  password: z.string().min(6, 'رمز عبور باید حداقل ۶ کاراکتر باشد'),
});

// اسکیما برای فرم ثبت نام (فرضی بر اساس استاندارد)
export const registerSchema = z.object({
  email: z.string().email('فرمت ایمیل صحیح نیست'),
  username: z.string().min(3, 'نام کاربری باید حداقل ۳ کاراکتر باشد'),
  password: z.string()
    .min(8, 'رمز عبور باید حداقل ۸ کاراکتر باشد')
    .regex(/[A-Z]/, 'باید شامل یک حرف بزرگ باشد')
    .regex(/[0-9]/, 'باید شامل یک عدد باشد'),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "رمز عبور و تکرار آن مطابقت ندارند",
  path: ["confirmPassword"],
});

// اسکیما برای تایید کد
export const verifySchema = z.object({
  code: z.string().length(4, 'کد تایید باید ۴ رقم باشد').regex(/^\d+$/, 'فقط عدد مجاز است'), // فرض بر 4 رقمی بودن
});