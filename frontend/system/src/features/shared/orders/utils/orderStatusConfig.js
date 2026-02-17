import { 
  Clock, PenTool, Printer, Truck, CheckCircle2, 
  XCircle, Archive, AlertCircle, Package 
} from "lucide-react";

export const ORDER_STATUSES = [
  {
    value: "PENDING_INITIAL_ADMIN",
    label: "در انتظار بررسی",
    icon: Clock,
    color: "text-amber-600 bg-amber-50 border-amber-200", // طلایی هشدار
  },
  {
    value: "DESIGNING_PROGRESS_DESIGNER",
    label: "در حال طراحی",
    icon: PenTool,
    color: "text-blue-600 bg-blue-50 border-blue-200", // آبی طراحی
  },
  {
    value: "DESIGN_REJECTED_REJECT_DESIGNER",
    label: "رد شده توسط طراح",
    icon: XCircle,
    color: "text-rose-600 bg-rose-50 border-rose-200", // قرمز خطا
  },
  {
    value: "PRINTING_PROGRESS_PRINT",
    label: "در حال چاپ",
    icon: Printer,
    color: "text-indigo-600 bg-indigo-50 border-indigo-200", // بنفش صنعتی
  },
  {
    value: "PRINT_REJECTED_REJECT_PRINT",
    label: "رد شده توسط چاپ",
    icon: AlertCircle,
    color: "text-rose-600 bg-rose-50 border-rose-200",
  },
  {
    value: "SENT_TO_WAREHOUSE_PROGRESS_LOGISTICS",
    label: "ارسال به انبار",
    icon: Truck,
    color: "text-cyan-600 bg-cyan-50 border-cyan-200",
  },
  {
    value: "RECEIVED_IN_WAREHOUSE_APPROVE_LOGISTICS",
    label: "رسید انبار",
    icon: Archive,
    color: "text-slate-600 bg-slate-100 border-slate-200",
  },
  {
    value: "WAREHOUSE_REJECTED_REJECT_LOGISTICS",
    label: "رد انبار",
    icon: XCircle,
    color: "text-rose-600 bg-rose-50 border-rose-200",
  },
  {
    value: "DELIVERED_APPROVE_LOGISTICS",
    label: "تحویل شده",
    icon: CheckCircle2,
    color: "text-emerald-600 bg-emerald-50 border-emerald-200", // سبز موفقیت
  },
  {
    value: "CANCELLED_CANCEL_ADMIN",
    label: "لغو شده",
    icon: XCircle,
    color: "text-gray-500 bg-gray-100 border-gray-200",
  },
];

// تابع کمکی برای پیدا کردن کانفیگ
export const getStatusConfig = (code) => {
  return ORDER_STATUSES.find((s) => s.value === code) || {
    label: code,
    icon: AlertCircle,
    color: "text-gray-600 bg-gray-50 border-gray-200",
  };
};