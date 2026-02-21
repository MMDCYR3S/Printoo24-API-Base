// src/app/features/admin/products/schemas/productSchemas.js
import { z } from 'zod';

// --- زیرمجموعه‌های مرحله ۱ ---

const ShellSchema = z.object({
  name: z.string().min(3, 'نام محصول باید حداقل ۳ کاراکتر باشد'),
  category_id: z.coerce.number().min(1, 'انتخاب دسته‌بندی الزامی است'),
  description: z.string().optional(),
  is_active: z.boolean().default(true),
  
  has_price: z.boolean().default(true),
  show_price: z.coerce.number().min(1, 'تعیین قیمت نمایشی برای کارت محصول الزامی است'),
  
  // قیمت رو اینجا optional می‌کنیم تا توی superRefine بر اساس نوع محصول بررسیش کنیم
  price: z.coerce.number().optional().default(0), 
  
  has_quantity: z.boolean().default(true), // true: تیراژی | false: تعدادی
  
  guide_text: z.string().nullable().optional(),
  guide_type: z.enum(['info', 'warning', 'danger', 'tip', 'success']).default('info'),
});

const PricingConfigSchema = z.object({
  base_setup_price: z.coerce.number().default(0), // هزینه ثابت پایه
  
  design_service_available: z.boolean().default(false),
  design_fee: z.coerce.number().default(0),

  // محدودیت‌های تعدادی (برای حالت has_quantity: false)
  min_quantity: z.coerce.number().optional(),
  max_quantity: z.coerce.number().optional(),
});

// آیتم‌های آرایه Quantities (تیراژها)
const QuantityTierSchema = z.object({
  id: z.coerce.number().min(1, 'انتخاب مقدار تیراژ الزامی است'),
  price: z.coerce.number().min(0, 'تعیین قیمت برای تیراژ الزامی است'), // اضافه شدن قیمت مختص تیراژ
  guide_text: z.string().optional(),
  guide_type: z.enum(['info', 'warning', 'danger', 'tip', 'success']).default('info'),
});

// آیتم‌های آرایه Sizes (سایزها)
const SizeSchema = z.object({
  id: z.coerce.number().min(1, 'انتخاب سایز الزامی است'),
  price_impact: z.coerce.number().default(0), // تاثیر روی قیمت
  guide_text: z.string().optional(),
  guide_type: z.enum(['info', 'warning', 'danger', 'tip', 'success']).default('info'),
});

// --- اسکیمای نهایی مرحله ۱ با اعتبارسنجی شرطی (Dynamic Validation) ---
export const ProductStep1Schema = z.object({
  shell: ShellSchema,
  pricing_config: PricingConfigSchema,
  quantities: z.array(QuantityTierSchema).optional().default([]),
  sizes: z.array(SizeSchema).optional().default([]),
}).superRefine((data, ctx) => {
  const isTirazhi = data.shell.has_quantity;

  if (isTirazhi) {
    // 🔴 اعتبارسنجی حالت تیراژی
    if (!data.quantities || data.quantities.length === 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "برای محصول تیراژی، تعریف حداقل یک تیراژ به همراه قیمت آن الزامی است.",
        path: ["quantities"], // ارور رو به فیلد تیراژها وصل می‌کنه
      });
    }
  } else {
    // 🔴 اعتبارسنجی حالت تعدادی/دونه‌ای
    if (data.shell.has_price && (!data.shell.price || data.shell.price <= 0)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "برای محصول تعدادی، تعیین قیمت پایه (دونه‌ای) الزامی است.",
        path: ["shell", "price"], // ارور رو مستقیماً به فیلد قیمت وصل می‌کنه
      });
    }
  }
});