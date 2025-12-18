// src/app/features/dashboard/categories/categorySchema.js
import { z } from 'zod';

// محدودیت حجم فایل (مثلاً ۲ مگابایت)
const MAX_FILE_SIZE = 2 * 1024 * 1024;
const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"];

// helper برای فایل (چون در ادیت ممکن است رشته URL باشد یا فایل جدید)
const imageSchema = z
  .any()
  .refine((file) => {
    if (!file) return true; // اختیاری
    if (typeof file === 'string') return true; // URL قبلی
    return file?.size <= MAX_FILE_SIZE;
  }, `حجم فایل باید کمتر از 2MB باشد.`)
  .refine((file) => {
    if (!file) return true;
    if (typeof file === 'string') return true;
    return ACCEPTED_IMAGE_TYPES.includes(file?.type);
  }, "فرمت فایل پشتیبانی نمی‌شود.");

export const categorySchema = z.object({
  name: z.string().min(2, "نام دسته‌بندی باید حداقل ۲ کاراکتر باشد"),
  slug: z.string().min(2, "Slug الزامی است").regex(/^[a-z0-9-]+$/, "فقط حروف انگلیسی کوچک، اعداد و خط تیره مجاز است"),
  parent: z.string().or(z.number()).nullable().optional(), // می‌تواند null باشد
  description: z.string().optional(),
  is_active: z.boolean().default(true),
  // فایل‌ها
  banner_wide: imageSchema.optional(),
  banner_box: imageSchema.optional(),
});