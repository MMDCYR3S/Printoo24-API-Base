import { z } from 'zod';

// 🔐 اسکیما برای فرم ورود
export const loginSchema = z.object({
  phone_number: z.string().min(1, 'ژمارەی تەلەفۆن پێویستە'),
  password: z.string().min(1, 'وشەی نهێنی پێویستە'),
});

// 📝 اسکیما برای فرم ثبت نام
export const registerSchema = z.object({
  first_name: z.string().min(2, 'ناو دەبێت لانیکەم ٢ پیت بێت'),
  last_name: z.string().min(2, 'ناوی سیانی دەبێت لانیکەم ٢ پیت بێت'),
  phone_number: z.string().regex(/^09[0-9]{9}$/, 'ژمارەی تەلەفۆن دەبێت ١١ ژمارە بێت'),
  password: z.string()
    .min(8, 'وشەی نهێنی دەبێت لانیکەم ٨ پیت بێت')
    .regex(/[A-Z]/, 'دەبێت لانیکەم یەک پیتی گەورەی تێدا بێت')
    .regex(/[0-9]/, 'دەبێت لانیکەم یەک ژمارەی تێدا بێت'),
  password_2: z.string()
}).refine((data) => data.password === data.password_2, {
  message: "وشەی نهێنی و دووبارەکردنەوەکەی یەک ناگرنەوە",
  path: ["password_2"],
});

// ✅ اسکیما برای تایید کد (در صورت نیاز در آینده)
export const verifySchema = z.object({
  code: z.string()
    .length(6, 'کۆدی پشتڕاستکردنەوە دەبێت ٦ ژمارە بێت')
    .regex(/^\d+$/, 'تەنها ژمارە بنووسە'),
});