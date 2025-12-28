import { z } from 'zod';

// --- زیرمجموعه‌های مرحله ۱ ---

const ShellSchema = z.object({
  name: z.string().min(3, 'نام محصول باید حداقل ۳ کاراکتر باشد'),
  category: z.coerce.number().min(1, 'انتخاب دسته‌بندی الزامی است'),
  slug: z.string().optional(), // معمولاً اتوماتیک ساخته می‌شود
  code: z.string().optional(),
  description: z.string().optional(),
  is_active: z.boolean().default(true),
  has_price: z.boolean().default(true),
  has_quantity: z.boolean().default(true), // آیا تیراژ دارد؟
  price: z.coerce.string().default("0"), // قیمت پایه نمایشی
  guide_text: z.string().nullable().optional(),
  guide_type: z.enum(['info', 'warning', 'danger', 'tip', 'success']).default('info'),
});

const PricingConfigSchema = z.object({
  base_setup_price: z.coerce.number().default(0), // هزینه اولیه (مثل زینک)
  design_service_available: z.boolean().default(false),
  design_fee: z.coerce.number().default(0),
  min_quantity: z.coerce.number().optional(),
  max_quantity: z.coerce.number().optional(),
  allow_custom_quantity: z.boolean().default(false),
});

const QuantityTierSchema = z.object({
  id: z.number().optional(), // برای ویرایش
  value: z.coerce.number().min(1, 'تعداد باید بیشتر از ۱ باشد'),
  price: z.coerce.number().min(0, 'قیمت نمی‌تواند منفی باشد'),
  guide_text: z.string().optional(),
  guide_type: z.string().default('info'),
});

const SizeSchema = z.object({
  id: z.coerce.number().min(1, 'انتخاب سایز الزامی است'), // شناسه سایز از دیتابیس
  price_impact: z.coerce.number().default(0), // افزایش قیمت برای این سایز
  guide_text: z.string().optional(),
});

// --- اسکیمای کلی مرحله ۱ (Create/Update) ---
export const ProductStep1Schema = z.object({
  shell: ShellSchema,
  pricing_config: PricingConfigSchema,
  quantities: z.array(QuantityTierSchema).optional(),
  sizes: z.array(SizeSchema).optional(),
}).refine((data) => {
  if (data.shell.has_quantity && (!data.quantities || data.quantities.length === 0)) {
    return false;
  }
  return true;
}, {
  message: "وقتی گزینه 'محصول تیراژدار' فعال است، باید حداقل یک تیراژ تعریف کنید.",
  path: ["quantities"],
});

// --- اسکیمای مرحله ۲ (Options) ---
export const OptionValueSchema = z.object({
  global_value_id: z.number().nullable().optional(), // اگر از بانک باشد
  label: z.string().optional(), // اگر کاستوم باشد یا اورراید
  value: z.string().optional(), // مقدار سیستمی
  price_impact: z.coerce.number().default(0),
  is_default: z.boolean().default(false),
});

export const ProductOptionSchema = z.object({
  option_id: z.number().nullable().optional(), // اگر از بانک انتخاب شده
  name: z.string().optional(), // نام سیستمی برای کاستوم
  label: z.string().min(1, 'عنوان ویژگی الزامی است'),
  input_type: z.enum(['select', 'radio', 'checkbox', 'text']).default('select'),
  is_required: z.boolean().default(false),
  guide_text: z.string().optional(),
  values_config: z.array(OptionValueSchema).min(1, 'حداقل یک مقدار تعریف کنید'),
});

export const ProductStep2Schema = z.object({
  options: z.array(ProductOptionSchema),
});