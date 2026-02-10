// src/app/features/dashboard/categorySchema.js
import { z } from 'zod';

const MAX_FILE_SIZE = 2 * 1024 * 1024;
const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"];

const imageSchema = z
  .any()
  .refine((file) => {
    if (!file) return true;
    if (typeof file === 'string') return true;
    return file?.size <= MAX_FILE_SIZE;
  }, `حجم فایل باید کمتر از 2MB باشد.`)
  .refine((file) => {
    if (!file) return true;
    if (typeof file === 'string') return true;
    return ACCEPTED_IMAGE_TYPES.includes(file?.type);
  }, "فرمت فایل پشتیبانی نمی‌شود.");

export const categorySchema = z.object({
  name: z.string().min(2, "نام دسته‌بندی باید حداقل ۲ کاراکتر باشد"),
  // slug کامل حذف شد
  parent: z.string().or(z.number()).nullable().optional(),
  description: z.string().optional(),
  is_active: z.boolean().default(true),
  banner_box: imageSchema.optional(),
  // banner_wide هم حذف شده بود
});