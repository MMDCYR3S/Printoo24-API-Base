import { z } from 'zod';

export const mediaSchema = z.object({
  file: z.any().refine((val) => val !== null && val !== undefined && val !== '', {
    message: 'انتخاب فایل رسانه الزامی است',
  }),
  is_active: z.boolean().default(true),
});