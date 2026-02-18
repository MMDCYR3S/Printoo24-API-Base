import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useDesignOrders } from "../../../hooks/useDesignOrders";
import { Button } from "@/components/ui/button";
import { ArrowRight, User, Package, Info, Clock, FileText, Tag, MapPin, Phone, Building2, Mail, AtSign, CheckCircle2, XCircle, CreditCard } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import DesignFileSection from "../components/DesignFileSection";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export default function DesignOrderDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { orderDetail, isDetailLoading, approve, reject, isActionLoading } = useDesignOrders(id);

  if (isDetailLoading) {
    return (
      <div className="p-8 space-y-6 max-w-7xl mx-auto">
        <Skeleton className="h-24 w-full rounded-2xl" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Skeleton className="lg:col-span-2 h-96 rounded-2xl" />
          <Skeleton className="h-96 rounded-2xl" />
        </div>
      </div>
    );
  }

  if (!orderDetail) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-slate-400">
        <Package size={64} className="mb-4 opacity-20" />
        <span className="text-xl font-black">سفارشی یافت نشد!</span>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-7xl mx-auto animate-in slide-in-from-bottom-4 fade-in duration-500">
      
      {/* 🟢 بخش اول: هدر اصلی و اکشن‌ها */}
      <div className="bg-white p-5 md:p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 sticky top-20 z-10">
        <div className="flex items-start md:items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => navigate(-1)} className="shrink-0 rounded-full h-10 w-10 border-slate-200 text-slate-500 hover:bg-slate-100 transition-all">
            <ArrowRight size={20} />
          </Button>
          <div className="flex flex-col gap-2">
            <div className="flex flex-wrap items-center gap-3">
               {/* ⭐️ نمایش اسم سفارش */}
               <h1 className="text-2xl font-black text-slate-900 tracking-tight">
                 {orderDetail.order_name || "بدون نام سفارش"}
               </h1>
               <Badge variant="outline" className="bg-slate-50 text-slate-600 border-slate-200 px-2.5 py-1 font-mono text-[11px] rounded-md tracking-wider">
                 {orderDetail.order_code}
               </Badge>
               <Badge className="bg-amber-100 text-amber-800 border-amber-200 font-bold px-3 py-1 text-xs">
                {orderDetail.current_status_display}
              </Badge>
            </div>
            
            <div className="flex flex-wrap items-center gap-4 text-xs font-bold text-slate-500">
              <span className="flex items-center gap-1.5 bg-slate-50 px-2 py-1 rounded-md">
                <Tag size={14} className="text-slate-400" /> {orderDetail.type_display}
              </span>
              <span className="flex items-center gap-1.5 bg-slate-50 px-2 py-1 rounded-md">
                <Clock size={14} className="text-slate-400" /> 
                {new Date(orderDetail.created_at).toLocaleString('fa-IR', { dateStyle: 'medium', timeStyle: 'short' })}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 w-full lg:w-auto">
          <Button 
            className="flex-1 lg:flex-none h-12 bg-emerald-600 hover:bg-emerald-700 text-white font-black px-8 shadow-lg shadow-emerald-600/20 transition-all gap-2 text-sm rounded-xl"
            onClick={() => approve(id)}
            disabled={isActionLoading}
          >
            <CheckCircle2 size={18} /> تایید و ارسال به مرحله بعد
          </Button>
          <Button 
            variant="outline" 
            className="flex-1 lg:flex-none h-12 border-rose-200 text-rose-600 hover:bg-rose-50 hover:border-rose-300 font-black px-6 transition-all gap-2 text-sm rounded-xl"
            onClick={() => {
              const reason = window.prompt("دلیل رد سفارش را بنویسید (نقص در فایل یا توضیحات):");
              if (reason) reject({ id, description: reason });
            }}
            disabled={isActionLoading}
          >
            <XCircle size={18} /> رد فایل
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* 🟢 ستون اصلی (سمت راست): توضیحات ادمین + جزئیات فنی آیتم‌ها */}
        <div className="lg:col-span-8 space-y-6">
          
          {/* ⭐️ نمایش توضیحات ادمین (Description) به صورت باکس هشدار زیبا */}
          {orderDetail.description && (
            <div className="bg-gradient-to-l from-blue-50 to-white border border-blue-100 p-5 rounded-2xl shadow-sm relative overflow-hidden">
              <div className="absolute left-0 top-0 h-full w-1 bg-blue-400"></div>
              <div className="flex gap-4 items-start">
                <div className="p-2.5 bg-blue-100 text-blue-600 rounded-xl shrink-0">
                  <FileText size={24} />
                </div>
                <div className="space-y-1.5">
                  <h3 className="text-sm font-black text-blue-900">توضیحات و دستورالعمل ادمین</h3>
                  <p className="text-sm font-medium text-blue-800/80 leading-loose whitespace-pre-wrap">
                    {orderDetail.description}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* ⭐️ لیست آیتم‌ها و ویژگی‌های داینامیک */}
          <div className="space-y-4">
            <h3 className="text-lg font-black text-slate-800 flex items-center gap-2 px-1">
              <Package className="text-gold-dark" size={20} />
              جزئیات فنی سفارش
            </h3>
            
            {orderDetail.items?.map((item, idx) => (
              <Card key={item.id} className="border-slate-200 shadow-sm rounded-2xl overflow-hidden">
                <div className="bg-slate-50 px-5 py-4 border-b border-slate-100 flex flex-wrap justify-between items-center gap-4">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center justify-center h-8 w-8 rounded-lg bg-slate-200 text-slate-600 font-black text-sm">
                      {idx + 1}
                    </span>
                    <span className="font-black text-slate-700 text-base">آیتم طراحی</span>
                  </div>
                  <div className="flex items-center gap-2">
                     <Badge variant="outline" className="font-mono bg-white border-slate-200 text-slate-600 px-3 py-1">
                       تعداد: {item.quantity}
                     </Badge>
                     {item.price && (
                       <Badge variant="secondary" className="font-bold text-slate-700 px-3 py-1">
                         فی: {Number(item.price).toLocaleString()} تومان
                       </Badge>
                     )}
                  </div>
                </div>
                
                <CardContent className="p-5 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    
                    {/* ⭐️ چاپ داینامیک ویژگی‌ها (Selections) */}
                    <div className="space-y-3">
                      <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-gold-dark" />
                        ویژگی‌ها و پارامترها
                      </h4>
                      <div className="bg-slate-50/50 rounded-xl border border-slate-100 p-2 grid grid-cols-1 gap-1.5">
                        {item.items && Object.entries(item.items).length > 0 ? (
                          Object.entries(item.items).map(([key, value]) => (
                            <div key={key} className="flex items-center justify-between bg-white p-3 rounded-lg border border-slate-100 shadow-[0_2px_10px_-4px_rgba(0,0,0,0.02)]">
                              <span className="text-xs font-bold text-slate-500">{key}</span>
                              <span className="text-xs font-black text-slate-800 text-left max-w-[60%] truncate" title={value}>
                                {value || "-"}
                              </span>
                            </div>
                          ))
                        ) : (
                          <div className="p-4 text-center text-xs text-slate-400 font-bold">بدون ویژگی ثبت شده</div>
                        )}
                      </div>
                    </div>

                    {/* فایل‌های ضمیمه */}
                    <div className="space-y-3">
                      <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                        فایل‌های ارسالی
                      </h4>
                      <DesignFileSection files={item.files} />
                    </div>
                  </div>

                  {/* یادداشت ادمین برای این آیتم خاص */}
                  {item.admin_note && (
                    <div className="bg-rose-50 border border-rose-100 p-4 rounded-xl flex gap-3 text-rose-800 text-xs font-bold leading-relaxed">
                      <Info size={18} className="shrink-0 text-rose-500" />
                      <p>یادداشت مهم ادمین: {item.admin_note}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* 🟢 ستون کناری (سمت چپ): اطلاعات جامع مشتری و مالی */}
        <div className="lg:col-span-4 space-y-6">
          
          {/* ⭐️ کارت اطلاعات مشتری (Customer Info + Recipient Info) */}
          <Card className="border-slate-200 shadow-sm rounded-2xl overflow-hidden">
            <CardHeader className="bg-slate-900 p-5">
              <CardTitle className="text-white text-base font-black flex items-center gap-2">
                <User className="text-gold-light" size={20} />
                اطلاعات مشتری و گیرنده
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              
              {/* بخش مشخصات اکانت (Customer Info) */}
              {orderDetail.customer_info && (
                <div className="p-5 bg-slate-50 border-b border-slate-100 space-y-3">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge className="bg-slate-200 text-slate-600 hover:bg-slate-200 pointer-events-none text-[10px]">حساب کاربری ثبت‌کننده</Badge>
                  </div>
                  <div className="flex items-center gap-3 text-sm font-bold text-slate-700">
                    <AtSign size={16} className="text-slate-400" />
                    {orderDetail.customer_info.username}
                  </div>
                  <div className="flex items-center gap-3 text-sm font-bold text-slate-700">
                    <Mail size={16} className="text-slate-400" />
                    {orderDetail.customer_info.email || "بدون ایمیل"}
                  </div>
                  {orderDetail.customer_info.company && (
                    <div className="flex items-center gap-3 text-sm font-bold text-slate-700">
                      <Building2 size={16} className="text-slate-400" />
                      {orderDetail.customer_info.company}
                    </div>
                  )}
                </div>
              )}

              {/* بخش مشخصات گیرنده و ارسال (Recipient) */}
              <div className="p-5 space-y-4">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline" className="bg-blue-50 text-blue-600 border-blue-200 text-[10px]">اطلاعات تحویل و گیرنده</Badge>
                </div>
                
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">نام گیرنده / مشتری</span>
                  <span className="text-sm font-black text-slate-800">{orderDetail.recipient_name}</span>
                </div>
                
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">تلفن تماس</span>
                  <div className="flex items-center gap-2 text-sm font-bold text-slate-800 bg-slate-50 w-fit px-3 py-1.5 rounded-lg border border-slate-100" dir="ltr">
                    <Phone size={14} className="text-slate-400" />
                    {orderDetail.recipient_phone}
                  </div>
                </div>

                {orderDetail.company_name && (
                  <div className="flex flex-col gap-1">
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">شرکت / مجموعه گیرنده</span>
                    <span className="text-sm font-black text-slate-800">{orderDetail.company_name}</span>
                  </div>
                )}

                <div className="flex flex-col gap-1 pt-2">
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter flex items-center gap-1">
                    <MapPin size={12} /> آدرس دقیق پستی
                  </span>
                  <span className="text-[11px] font-bold text-slate-600 leading-loose bg-slate-50 p-3 rounded-xl border border-slate-100">
                    {orderDetail.full_address}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* ⭐️ کارت خلاصه مالی (فقط جهت اطلاع طراح) */}
          <Card className="border-slate-200 shadow-sm rounded-2xl bg-white">
            <CardContent className="p-5 space-y-4">
              <h3 className="text-xs font-black text-slate-400 flex items-center gap-2 border-b border-slate-100 pb-3">
                <CreditCard size={16} />
                ارزش مالی سفارش (خلاصه)
              </h3>
              
              <div className="flex justify-between items-center">
                 <span className="text-xs font-bold text-slate-500">مبلغ پایه محصولات:</span>
                 <span className="text-sm font-black text-slate-700">
                   {Number(orderDetail.base_products_price).toLocaleString()} <span className="text-[10px] font-normal text-slate-400">تومان</span>
                 </span>
              </div>
              
              <div className="flex justify-between items-center bg-green-50/50 p-3 rounded-xl border border-green-100">
                 <span className="text-xs font-black text-green-700">مبلغ کل سفارش:</span>
                 <span className="text-lg font-black text-green-700 tracking-tight">
                   {Number(orderDetail.total_price).toLocaleString()} <span className="text-[10px] font-bold text-green-600/60">تومان</span>
                 </span>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
}