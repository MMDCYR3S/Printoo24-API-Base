// src/app/features/admin/products/schemas/productSchemas.js
import { z } from 'zod';

// --- زیرمجموعه‌های مرحله ۱ ---

const ShellSchema = z.object({
  name: z.string().min(3, 'نام محصول باید حداقل ۳ کاراکتر باشد'),
  category_id: z.coerce.number().min(1, 'انتخاب دسته‌بندی الزامی است'),
  // اسلاگ را حذف کردیم چون گفتید بکند می‌سازد
  description: z.string().optional(),
  is_active: z.boolean().default(true),
  
  has_price: z.boolean().default(true),
  price: z.coerce.string().default("0"), // قیمت پایه واحد (مهم‌ترین فیلد)
  
  has_quantity: z.boolean().default(true), // true: تیراژی (لیستی) | false: تعدادی (آزاد)
  
  guide_text: z.string().nullable().optional(),
  guide_type: z.enum(['info', 'warning', 'danger', 'tip', 'success']).default('info'),
});

const PricingConfigSchema = z.object({
  base_setup_price: z.coerce.number().default(0), // هزینه ثابت (یکبار جمع می‌شود)
  
  // بخش طراحی (جدید)
  design_service_available: z.boolean().default(false),
  design_fee: z.coerce.number().default(0),

  // محدودیت‌های تعدادی
  min_quantity: z.coerce.number().optional(),
  max_quantity: z.coerce.number().optional(),
});

// آیتم‌های آرایه Quantities (دیگر قیمت ندارد! فقط رفرنس به ID و راهنما)
const QuantityTierSchema = z.object({
  id: z.coerce.number().min(1, 'انتخاب مقدار تیراژ الزامی است'), // ID از مستر دیتا
  guide_text: z.string().optional(),
  guide_type: z.enum(['info', 'warning', 'danger', 'tip', 'success']).default('info'),
});

const SizeSchema = z.object({
  id: z.coerce.number().min(1, 'انتخاب سایز الزامی است'),
  price_impact: z.coerce.number().default(0), // تاثیر روی قیمت واحد
  guide_text: z.string().optional(),
  guide_type: z.enum(['info', 'warning', 'danger', 'tip', 'success']).default('info'),
});

// --- اسکیمای نهایی مرحله ۱ ---
export const ProductStep1Schema = z.object({
  shell: ShellSchema,
  pricing_config: PricingConfigSchema,
  quantities: z.array(QuantityTierSchema).optional(),
  sizes: z.array(SizeSchema).optional(),
}).superRefine((data, ctx) => {
  // اگر تیراژی است، لیست تیراژ نباید خالی باشد
  if (data.shell.has_quantity) {
    if (!data.quantities || data.quantities.length === 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "در حالت تیراژی، باید حداقل یک گزینه تیراژ (مثلاً ۱۰۰۰ تایی) انتخاب کنید.",
        path: ["quantities"],
      });
    }
  } 
});