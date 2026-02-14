import { z } from "zod";

// ==========================================
// 1. اسکیمای آیتم‌های سفارش
// ==========================================
const selectionSchema = z.record(z.string(), z.any()).optional();

const orderItemSchema = z.object({
  name: z.string().min(2, "نام محصول الزامی است"),
  description: z.string().optional(),
  
  quantity: z.coerce.number().min(1, "تعداد حداقل ۱ باشد"),
  item_price: z.coerce.number().min(0, "قیمت واحد نمی‌تواند منفی باشد"),
  
  selections: selectionSchema, 
});

// ==========================================
// 2. اسکیمای فرم اصلی ثبت سفارش
// ==========================================
export const createOrderSchema = z.object({
  user_id: z.coerce.number({ required_error: "انتخاب مشتری الزامی است" }).min(1, "مشتری را انتخاب کنید"),
  
  full_address: z.string().min(5, "آدرس کامل الزامی است"),
  recipient_name: z.string().optional(),
  recipient_phone: z.string().optional(),
  company_name: z.string().optional(),

  price: z.coerce.number().min(1000, "مبلغ کل نامعتبر است"),
  items: z.array(orderItemSchema).min(1, "حداقل یک آیتم اضافه کنید"),
});

// ==========================================
// 3. اسکیمای ثبت سریع مشتری (که پاک شده بود)
// ==========================================
export const quickCustomerSchema = z.object({
  first_name: z.string().min(2, "نام وارد نشده"),
  last_name: z.string().min(2, "نام خانوادگی وارد نشده"),
  phone_number: z
    .string()
    .regex(/^09[0-9]{9}$/, "شماره موبایل معتبر نیست"),
  company: z.string().optional(),
  
  // فیلدهای اختیاری یا سیستمی
  username: z.string().optional(),
  email: z.string().optional(),
  password: z.string().optional(),
});