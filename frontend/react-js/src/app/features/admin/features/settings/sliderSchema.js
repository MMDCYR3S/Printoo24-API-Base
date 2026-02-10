// src/app/features/settings/schemas/sliderSchema.js
import { z } from 'zod';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"];

const imageSchema = z
  .any()
  .refine((file) => {
    if (!file) return false; // تصویر اجباری است (مگر در ادیت که هندل میکنیم)
    if (typeof file === 'string') return true; // URL معتبر است
    return file?.size <= MAX_FILE_SIZE;
  }, `حجم تصویر باید کمتر از 5 مگابایت باشد.`)
  .refine((file) => {
    if (typeof file === 'string') return true;
    return ACCEPTED_IMAGE_TYPES.includes(file?.type);
  }, "فرمت فایل باید jpg, png یا webp باشد.");

export const sliderSchema = z.object({
  name: z.string().min(2, "عنوان اسلایدر الزامی است"),
  image: imageSchema,
});