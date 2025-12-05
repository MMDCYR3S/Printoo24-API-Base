import { z } from 'zod';

// 🔐 اسکیما برای فرم ورود
export const loginSchema = z.object({
  username: z.string().min(1, 'نام کاربری الزامی است'),
  password: z.string().min(1, 'رمز عبور الزامی است'),
});

// 📝 اسکیما برای فرم ثبت نام
export const registerSchema = z.object({
  email: z.string().email('فرمت ایمیل صحیح نیست'),
  username: z.string().min(3, 'نام کاربری باید حداقل ۳ کاراکتر باشد'),
  password: z.string()
    .min(8, 'رمز عبور باید حداقل ۸ کاراکتر باشد')
    .regex(/[A-Z]/, 'باید شامل یک حرف بزرگ باشد')
    .regex(/[0-9]/, 'باید شامل یک عدد باشد'),
  password_2: z.string()
}).refine((data) => data.password === data.password_2, {
  message: "رمز عبور و تکرار آن مطابقت ندارند",
  path: ["password_2"],
});

// ✅ اسکیما برای تایید کد (Verify)
export const verifySchema = z.object({
  email: z.string().email('ایمیل نامعتبر است').optional(), // اختیاری چون شاید از URL بیاید
  code: z.string()
    .length(4, 'کد تایید باید ۴ رقم باشد')
    .regex(/^\d+$/, 'فقط عدد وارد کنید'),
});