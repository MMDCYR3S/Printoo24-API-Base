import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { orderService } from "@/features/shared/orders/api/orderService";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  ArrowRight, Printer, User, MapPin, Phone, 
  Calendar, CreditCard, Box, Activity, FileText 
} from "lucide-react";
import StatusChangeCell from "@/features/shared/orders/components/StatusChangeCell";
import { Skeleton } from "@/components/ui/skeleton";

// --- ابزارهای کمکی (Helpers) ---

// پارسر هوشمند برای تبدیل رشته‌های پایتونی به آبجکت جاوااسکریپت
const parsePythonDict = (str) => {
  if (!str) return {};
  try {
    // تلاش برای تبدیل ' به " جهت استانداردسازی JSON
    const validJson = str.replace(/'/g, '"').replace(/False/g, "false").replace(/True/g, "true");
    return JSON.parse(validJson);
  } catch (e) {
    console.error("Failed to parse spec:", str);
    return {};
  }
};

// فرمت کننده قیمت
const formatPrice = (price) => Number(price).toLocaleString() + " تومان";

// --- کامپوننت اصلی ---
const OrderDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: order, isLoading, isError } = useQuery({
    queryKey: ["order", id],
    queryFn: () => orderService.getOrderById(id),
  });

  if (isLoading) return <OrderDetailSkeleton />;
  if (isError) return <div className="p-10 text-center text-red-500 font-bold">خطا در دریافت اطلاعات سفارش</div>;

  // استخراج لاگ‌ها و مشخصات فنی از اولین آیتم (چون معمولا مشخصات در آیتم‌هاست)
  const firstItem = order.items?.[0] || {};
  const attributes = firstItem.specifications?.attributes || [];
  
  // پیدا کردن لاگ‌ها از بین ویژگی‌ها
  const logAttribute = attributes.find(attr => attr.label === "Admin Logs");
  const rawLogs = logAttribute ? logAttribute.value : "[]";
  const logs = rawLogs.replace(/[\[\]']/g, "").split(",").filter(l => l.trim().length > 0);

  // پیدا کردن مشخصات فنی
  const specAttribute = attributes.find(attr => attr.label === "Specifications");
  const specs = parsePythonDict(specAttribute?.value);

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto pb-20">
      
      {/* 1. نوار ابزار بالا (Top Bar) */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 rounded-md border border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => navigate(-1)} className="text-slate-500 hover:text-slate-800">
            <ArrowRight className="h-5 w-5" />
          </Button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black text-slate-800 flex items-center gap-2">
                سفارش <span className="font-mono text-xl text-gold-dark">{order.order_code}</span>
              </h1>
              <Badge variant="outline" className="rounded-sm bg-slate-50 text-slate-600 border-slate-200">
                {order.type === "2" ? "اختصاصی" : "سیستمی"}
              </Badge>
            </div>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
              <Calendar className="h-3 w-3" />
              ثبت شده در: {new Date(order.created_at).toLocaleDateString('fa-IR')} - ساعت {new Date(order.created_at).toLocaleTimeString('fa-IR', {hour: '2-digit', minute:'2-digit'})}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
            {/* دکمه پرینت فاکتور (بعدا فانکشنال میشه) */}
            <Button variant="outline" className="h-9 gap-2 border-slate-300 text-slate-600">
                <Printer className="h-4 w-4" />
                چاپ فاکتور
            </Button>
            
            {/* تغییر وضعیت سریع */}
            <div className="w-[200px]">
                <StatusChangeCell orderId={order.id} currentStatus={order.status_name} />
            </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* 2. ستون اصلی (اقلام و مشخصات) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* کارت اقلام سفارش */}
          <div className="bg-white rounded-md border border-slate-200 shadow-sm overflow-hidden">
            <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex justify-between items-center">
              <h2 className="font-bold text-slate-700 flex items-center gap-2">
                <Box className="h-4 w-4 text-gold-dark" />
                اقلام سفارش ({order.items.length})
              </h2>
            </div>
            <div className="divide-y divide-slate-100">
              {order.items.map((item) => (
                <div key={item.id} className="p-4 hover:bg-slate-50/50 transition-colors">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-bold text-slate-800 text-base">{item.name_display}</h3>
                      <div className="text-xs text-slate-500 mt-1">شناسه آیتم: #{item.id}</div>
                    </div>
                    <div className="text-left">
                      <div className="font-black text-slate-800">{formatPrice(item.price)}</div>
                      <div className="text-xs text-slate-400 mt-1">تعداد: {item.quantity.toLocaleString()} عدد</div>
                    </div>
                  </div>
                  
                  {/* مشخصات فنی پارس شده */}
                  <div className="bg-slate-50 rounded-sm border border-slate-200 p-3 grid grid-cols-2 md:grid-cols-4 gap-y-3 gap-x-4">
                    {Object.entries(specs).map(([key, value]) => (
                        <div key={key} className="flex flex-col">
                            <span className="text-[10px] text-slate-400 uppercase font-bold mb-0.5">{key}</span>
                            <span className="text-xs text-slate-700 font-medium truncate" title={value}>{value}</span>
                        </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* کارت لاگ‌های سیستم (Timeline) */}
          <div className="bg-white rounded-md border border-slate-200 shadow-sm">
            <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
              <h2 className="font-bold text-slate-700 flex items-center gap-2">
                <Activity className="h-4 w-4 text-blue-500" />
                تاریخچه عملیات
              </h2>
            </div>
            <div className="p-4">
               <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
                  {logs.length > 0 ? logs.map((log, index) => (
                      <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                          <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-slate-100 group-[.is-active]:bg-gold-light group-[.is-active]:text-gold-dark shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                              <FileText className="h-4 w-4" />
                          </div>
                          <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-3 rounded border border-slate-200 bg-white shadow-sm">
                              <div className="text-xs font-medium text-slate-600">{log}</div>
                          </div>
                      </div>
                  )) : (
                      <div className="text-center text-xs text-slate-400 py-4">هنوز لاگی ثبت نشده است.</div>
                  )}
               </div>
            </div>
          </div>

        </div>

        {/* 3. ستون کناری (مشتری و مالی) */}
        <div className="space-y-6">
          
          {/* کارت اطلاعات مشتری */}
          <div className="bg-white rounded-md border border-slate-200 shadow-sm">
            <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
              <h2 className="font-bold text-slate-700 flex items-center gap-2">
                <User className="h-4 w-4 text-slate-500" />
                اطلاعات مشتری
              </h2>
            </div>
            <div className="p-4 space-y-4">
              <div className="flex items-center gap-3">
                 <div className="h-12 w-12 rounded-md bg-slate-100 flex items-center justify-center text-slate-500 font-bold text-lg">
                    {order.recipient_name?.substring(0,1)}
                 </div>
                 <div>
                    <div className="font-bold text-slate-800">{order.recipient_name}</div>
                    {order.company_name && <div className="text-xs text-slate-500 mt-0.5">{order.company_name}</div>}
                 </div>
              </div>
              <Separator />
              <div className="space-y-3">
                  <div className="flex items-start gap-3 text-sm">
                      <Phone className="h-4 w-4 text-slate-400 mt-0.5" />
                      <span className="font-mono dir-ltr">{order.recipient_phone}</span>
                  </div>
                  <div className="flex items-start gap-3 text-sm">
                      <MapPin className="h-4 w-4 text-slate-400 mt-0.5" />
                      <span className="text-slate-600 leading-relaxed">
                          {order.full_address || order.address_detail || "آدرسی ثبت نشده است"}
                      </span>
                  </div>
              </div>
            </div>
          </div>

          {/* کارت مالی */}
          <div className="bg-white rounded-md border border-slate-200 shadow-sm">
            <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
              <h2 className="font-bold text-slate-700 flex items-center gap-2">
                <CreditCard className="h-4 w-4 text-emerald-600" />
                وضعیت مالی
              </h2>
            </div>
            <div className="p-4 space-y-3">
                <div className="flex justify-between items-center">
                    <span className="text-slate-500 text-sm">مبلغ کل سفارش</span>
                    <span className="font-black text-slate-800 text-lg">{formatPrice(order.total_price)}</span>
                </div>
                {/* در آینده اگر پرداخت اقساطی داشتیم اینجا اضافه میشود */}
                <div className="bg-emerald-50 text-emerald-700 text-xs px-3 py-2 rounded-sm border border-emerald-100 text-center font-bold">
                    پرداخت شده (فرض سیستم)
                </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

// اسکلتون لودینگ (برای زیبایی)
const OrderDetailSkeleton = () => (
    <div className="space-y-6 max-w-7xl mx-auto">
        <div className="h-16 bg-slate-100 rounded-md w-full animate-pulse"></div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
                <div className="h-64 bg-slate-100 rounded-md animate-pulse"></div>
                <div className="h-40 bg-slate-100 rounded-md animate-pulse"></div>
            </div>
            <div className="space-y-6">
                <div className="h-52 bg-slate-100 rounded-md animate-pulse"></div>
                <div className="h-40 bg-slate-100 rounded-md animate-pulse"></div>
            </div>
        </div>
    </div>
);

export default OrderDetail;