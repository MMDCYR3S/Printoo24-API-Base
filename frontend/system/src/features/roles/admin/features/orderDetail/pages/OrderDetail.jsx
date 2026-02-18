import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { orderService } from "@/features/shared/orders/api/orderService";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  ArrowRight, Printer, MapPin, Phone, Calendar, 
  CreditCard, Box, Hash, Copy, Truck, UserCircle, 
  Clock, CheckCircle2, AlertCircle 
} from "lucide-react";
import StatusChangeCell from "@/features/shared/orders/components/StatusChangeCell";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

// --- توابع کمکی ---
const formatPrice = (price) => Number(price).toLocaleString();
const copyToClipboard = (text) => {
    if(!text) return;
    navigator.clipboard.writeText(text);
    toast.success("کپی شد");
};

const OrderDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: order, isLoading, isError } = useQuery({
    queryKey: ["order", id],
    queryFn: () => orderService.getOrderById(id),
  });

  if (isLoading) return <OrderDetailSkeleton />;
  if (isError) return (
    <div className="flex flex-col items-center justify-center h-[50vh] text-slate-400 gap-4">
        <AlertCircle className="h-10 w-10 text-rose-400" />
        <p className="font-bold">خطا در دریافت اطلاعات سفارش</p>
        <Button onClick={() => window.location.reload()} variant="outline">تلاش مجدد</Button>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50/50 pb-20 animate-in fade-in duration-500">
      
      {/* 1. HERO SECTION: هدر تیره و جذاب برای اطلاعات کلیدی */}
      <div className="bg-slate-900 text-white pt-8 pb-12 px-6 shadow-lg mb-[-40px]">
        <div className="max-w-[1600px] mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={() => navigate(-1)} className="text-slate-300 hover:text-white hover:bg-white/10 rounded-full">
                        <ArrowRight className="h-6 w-6" />
                    </Button>
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <h1 className="text-2xl font-black tracking-tight">
                                سفارش <span className="font-mono text-gold-light select-all cursor-pointer" onClick={() => copyToClipboard(order.order_code)}>{order.order_code}</span>
                            </h1>
                            <Badge className="bg-white/10 hover:bg-white/20 text-white border-0 backdrop-blur-md">
                                {order.type === "2" ? "اختصاصی" : "سیستمی"}
                            </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-xs text-slate-400 font-medium">
                            <span className="flex items-center gap-1.5">
                                <Calendar className="h-3.5 w-3.5" />
                                {new Date(order.created_at).toLocaleDateString('fa-IR')}
                            </span>
                            <span className="flex items-center gap-1.5">
                                <Clock className="h-3.5 w-3.5" />
                                {new Date(order.created_at).toLocaleTimeString('fa-IR', {hour: '2-digit', minute:'2-digit'})}
                            </span>
                        </div>
                    </div>
                </div>

                {/* بخش عملیات سریع (Status & Print) */}
                <div className="flex items-center gap-3 bg-white/5 p-1.5 rounded-lg border border-white/10 backdrop-blur-sm">
                    <div className="w-[200px]">
                        {/* اینجا کامپوننت وضعیت رو کمی شفاف و دارک میکنیم با کلاس کاستوم اگر ساپورت کنه، یا استاندارد میذاریم */}
                        <StatusChangeCell orderId={order.id} currentStatus={order.status_name} />
                    </div>
                    <Separator orientation="vertical" className="h-8 bg-white/10" />
                    <Button variant="ghost" size="icon" className="text-slate-300 hover:text-white hover:bg-white/10" title="چاپ فاکتور">
                        <Printer className="h-5 w-5" />
                    </Button>
                </div>
            </div>
        </div>
      </div>

      {/* 2. GRID LAYOUT: چیدمان کارت‌ها */}
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
            
            {/* ستون چپ (اطلاعات مشتری و مالی) - عرض کمتر */}
            <div className="xl:col-span-4 space-y-6">
                
                {/* کارت مشتری (Customer Card) */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden group hover:border-blue-300/50 transition-colors">
                    <div className="p-6">
                        <div className="flex items-start justify-between mb-6">
                            <div className="flex items-center gap-4">
                                <div className="h-14 w-14 rounded-full bg-slate-50 border-2 border-slate-100 flex items-center justify-center text-slate-400 shadow-inner">
                                    <UserCircle className="h-8 w-8" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-slate-800 text-lg">{order.recipient_name}</h3>
                                    <p className="text-xs text-slate-500 font-medium mt-1">
                                        {order.company_name || "مشتری حقیقی"}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="group/item bg-slate-50 p-3 rounded-lg border border-slate-100 flex justify-between items-center hover:bg-blue-50 hover:border-blue-100 transition-colors cursor-pointer" onClick={() => copyToClipboard(order.recipient_phone)}>
                                <div className="flex items-center gap-3">
                                    <div className="bg-white p-2 rounded text-slate-400 group-hover/item:text-blue-500 transition-colors">
                                        <Phone className="h-4 w-4" />
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[10px] text-slate-400 font-bold uppercase">شماره تماس</span>
                                        <span className="font-mono text-sm font-bold text-slate-700 dir-ltr">{order.recipient_phone}</span>
                                    </div>
                                </div>
                                <Copy className="h-3.5 w-3.5 text-slate-300 opacity-0 group-hover/item:opacity-100 transition-opacity" />
                            </div>

                            <div className="group/item bg-slate-50 p-3 rounded-lg border border-slate-100 flex gap-3 hover:bg-amber-50 hover:border-amber-100 transition-colors">
                                <div className="bg-white p-2 rounded text-slate-400 group-hover/item:text-amber-500 transition-colors h-fit">
                                    <MapPin className="h-4 w-4" />
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-[10px] text-slate-400 font-bold uppercase">آدرس تحویل</span>
                                    <p className="text-sm text-slate-600 leading-relaxed mt-0.5 text-justify">
                                        {order.full_address || order.address_detail || "---"}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* کارت مالی (Financial Summary) */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                    <div className="bg-slate-50/50 px-6 py-4 border-b border-slate-100 flex justify-between items-center">
                        <h3 className="font-bold text-slate-700 text-sm flex items-center gap-2">
                            <CreditCard className="h-4 w-4 text-emerald-500" />
                            جزئیات پرداخت
                        </h3>
                        <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 text-[10px] px-2 h-5">
                            تایید شده
                        </Badge>
                    </div>
                    <div className="p-6 space-y-4">
                        <div className="flex justify-between items-center">
                            <span className="text-slate-500 text-sm">مبلغ کل اقلام</span>
                            <span className="font-bold text-slate-800">{formatPrice(order.total_price)}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-slate-500 text-sm">مالیات / خدمات</span>
                            <span className="font-bold text-slate-400 text-sm">0</span>
                        </div>
                        <Separator className="my-2" />
                        <div className="flex justify-between items-end">
                            <span className="text-slate-800 font-bold text-base">مبلغ نهایی</span>
                            <div className="text-right">
                                <span className="block font-black text-2xl text-slate-900 tracking-tight">{formatPrice(order.total_price)}</span>
                                <span className="text-[10px] text-slate-400 font-bold">تومان - پرداخت آنلاین</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* ستون راست (اقلام سفارش) - عرض بیشتر */}
            <div className="xl:col-span-8 space-y-6">
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden min-h-[400px]">
                    <div className="px-6 py-5 border-b border-slate-100 flex justify-between items-center bg-white sticky top-0 z-10">
                        <div className="flex items-center gap-3">
                            <div className="bg-gold-light/20 p-2 rounded-lg text-gold-dark">
                                <Box className="h-5 w-5" />
                            </div>
                            <div>
                                <h2 className="font-bold text-slate-800 text-lg">لیست اقلام سفارش</h2>
                                <p className="text-xs text-slate-400 font-medium">شامل {order.items.length} ردیف محصول</p>
                            </div>
                        </div>
                    </div>

                    <div className="divide-y divide-slate-100">
                        {order.items.map((item, index) => (
                            <div key={item.id} className="p-6 hover:bg-slate-50/50 transition-colors group">
                                <div className="flex flex-col md:flex-row gap-6">
                                    {/* شماره ردیف و تعداد */}
                                    <div className="flex flex-col items-center gap-2 min-w-[60px]">
                                        <span className="text-[10px] text-slate-300 font-bold">#{index + 1}</span>
                                        <div className="h-12 w-16 bg-slate-100 rounded-lg flex items-center justify-center border border-slate-200 text-slate-600 font-black text-lg shadow-inner">
                                            {item.quantity}
                                        </div>
                                        <span className="text-[10px] text-slate-400">عدد</span>
                                    </div>

                                    {/* جزئیات اصلی */}
                                    <div className="flex-1 space-y-4">
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <h3 className="font-bold text-slate-800 text-lg">{item.name_display}</h3>
                                                <div className="flex items-center gap-2 mt-1">
                                                    <span className="bg-slate-100 text-slate-500 text-[10px] px-2 py-0.5 rounded font-mono">ID: {item.id}</span>
                                                </div>
                                            </div>
                                            <div className="text-left">
                                                <div className="font-black text-slate-700 text-lg">{formatPrice(item.price)}</div>
                                            </div>
                                        </div>

                                        {/* مشخصات فنی (Grid Layout) */}
                                        {item.specifications?.attributes?.length > 0 && (
                                            <div className="bg-slate-50 rounded-xl border border-slate-200/60 p-4 relative overflow-hidden">
                                                <div className="absolute top-0 right-0 bg-slate-200 text-slate-500 text-[9px] px-2 py-0.5 rounded-bl-lg font-bold">
                                                    مشخصات فنی
                                                </div>
                                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-y-4 gap-x-8 pt-2">
                                                    {item.specifications.attributes.map((attr, idx) => (
                                                        <div key={idx} className="flex flex-col">
                                                            <span className="text-[10px] text-slate-400 font-bold mb-1 flex items-center gap-1">
                                                                <span className="w-1 h-1 rounded-full bg-gold-dark inline-block"></span>
                                                                {attr.label}
                                                            </span>
                                                            <span className="text-sm text-slate-700 font-medium break-words leading-snug">
                                                                {attr.value}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* لاگ‌های لجستیک یا توضیحات اضافه (Optional) */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center gap-4 text-slate-500 text-sm border-l-4 border-l-blue-500">
                    <Truck className="h-5 w-5 text-blue-500" />
                    <p>این سفارش نیاز به بسته‌بندی ضدضربه دارد (توضیحات سیستمی تستی).</p>
                </div>
            </div>

        </div>
      </div>
    </div>
  );
};

// --- اسکلتون لودینگ (Skeleton) ---
const OrderDetailSkeleton = () => (
    <div className="min-h-screen bg-slate-50">
        <div className="h-48 bg-slate-200 w-full animate-pulse mb-8"></div>
        <div className="max-w-[1600px] mx-auto px-6 grid grid-cols-1 xl:grid-cols-12 gap-6">
            <div className="xl:col-span-4 space-y-6">
                <div className="h-64 bg-slate-200 rounded-xl animate-pulse"></div>
                <div className="h-40 bg-slate-200 rounded-xl animate-pulse"></div>
            </div>
            <div className="xl:col-span-8">
                <div className="h-[500px] bg-slate-200 rounded-xl animate-pulse"></div>
            </div>
        </div>
    </div>
);

export default OrderDetail;