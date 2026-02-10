// src/app/features/settings/schemas/modalSchema.js
import { z } from 'zod';

const MAX_FILE_SIZE = 2 * 1024 * 1024; // 2MB
const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"];

const imageSchema = z
  .any()
  .refine((file) => {
    if (!file) return true; // اختیاری
    if (typeof file === 'string') return true;
    return file?.size <= MAX_FILE_SIZE;
  }, `حجم تصویر باید کمتر از 2 مگابایت باشد.`)
  .refine((file) => {
    if (!file) return true;
    if (typeof file === 'string') return true;
    return ACCEPTED_IMAGE_TYPES.includes(file?.type);
  }, "فرمت فایل پشتیبانی نمی‌شود.");

export const modalSchema = z.object({
  title: z.string().min(2, "عنوان مودال الزامی است"),
  description: z.string().optional(),
  image: imageSchema.optional(),
  cta_text: z.string().optional(), // متن دکمه (مثلا: مشاهده محصول)
  cta_url: z.string().optional(),  // لینک دکمه
  is_active: z.boolean().default(true),
}).refine(data => {
    // اگر متن دکمه هست، لینک هم باید باشد و برعکس (Validation ترکیبی)
    if (data.cta_text && !data.cta_url) return false;
    if (!data.cta_text && data.cta_url) return false;
    return true;
}, {
    message: "در صورت وارد کردن دکمه، هم متن و هم لینک الزامی است",
    path: ["cta_url"], // ارور را روی فیلد لینک نشان بده
});