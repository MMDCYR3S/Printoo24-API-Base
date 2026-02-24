import { z } from 'zod';

// 🔐 اسکیما برای فرم ورود
export const loginSchema = z.object({
  phone_number: z.string().min(1, 'شماره تلفن الزامی است'),
  password: z.string().min(1, 'رمز عبور الزامی است'),
});

// 📝 اسکیما برای فرم ثبت نام
export const registerSchema = z.object({
  first_name: z.string().min(2, 'نام باید حداقل ۲ کاراکتر باشد'),
  last_name: z.string().min(2, 'نام خانوادگی باید حداقل ۲ کاراکتر باشد'),
  phone_number: z.string().regex(/^09[0-9]{9}$/, 'شماره تلفن باید ۱۱ رقم شروع شود'),
  password: z.string()
    .min(8, 'رمز عبور باید حداقل ۸ کاراکتر باشد')
    .regex(/[A-Z]/, 'باید شامل یک حرف بزرگ باشد')
    .regex(/[0-9]/, 'باید شامل یک عدد باشد'),
  password_2: z.string()
}).refine((data) => data.password === data.password_2, {
  message: "رمز عبور و تکرار آن مطابقت ندارند",
  path: ["password_2"],
});

// ✅ اسکیما برای تایید کد (در صورت نیاز در آینده)
export const verifySchema = z.object({
  code: z.string()
    .length(6, 'کد تایید باید ۶ رقم باشد')
    .regex(/^\d+$/, 'فقط عدد وارد کنید'),
});