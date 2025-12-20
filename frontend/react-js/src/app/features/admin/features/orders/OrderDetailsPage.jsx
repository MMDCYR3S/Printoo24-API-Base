import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowRight, User, MapPin, Calendar, CreditCard, 
  FileText, Download, Printer, Box, AlertTriangle 
} from 'lucide-react';
import { useAdminOrderDetails } from '../../hooks/useAdminOrderDetails';
import OrderStatusBadge from './components/OrderStatusBadge';
import { formatPrice } from '../../../utils/formatPrice';

const OrderDetailsPage = () => {
  const navigate = useNavigate();
  const { order, isLoading, isError } = useAdminOrderDetails();

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center h-[60vh]">
      <span className="loading loading-spinner loading-lg text-primary"></span>
      <p className="mt-4 text-slate-400">در حال بارگذاری جزئیات سفارش...</p>
    </div>
  );

  if (isError || !order) return (
    <div className="alert alert-error max-w-md mx-auto mt-10">
      <AlertTriangle />
      <span>خطا در دریافت اطلاعات سفارش. لطفاً دوباره تلاش کنید.</span>
      <button onClick={() => navigate(-1)} className="btn btn-sm">بازگشت</button>
    </div>
  );

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 pb-20">
      
      {/* --- Header --- */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="btn btn-circle btn-ghost btn-sm">
            <ArrowRight size={20} />
          </button>
          <div>
            <h1 className="text-2xl font-black text-slate-800 flex items-center gap-3">
              سفارش #{order.id}
              <OrderStatusBadge status={order.status_info} />
            </h1>
            <p className="text-slate-500 text-sm mt-1 flex items-center gap-2">
              <Calendar size={14}/>
              ثبت شده در {new Date(order.created_at).toLocaleDateString('fa-IR', { dateStyle: 'long' })} ساعت {new Date(order.created_at).toLocaleTimeString('fa-IR', {timeStyle: 'short'})}
            </p>
          </div>
        </div>
        
        <div className="flex gap-2">
          <button className="btn btn-outline gap-2">
            <Printer size={18} />
            چاپ فاکتور
          </button>
          {/* دکمه‌های عملیاتی مثل تغییر وضعیت رو بعداً اینجا میشه اضافه کرد */}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* --- Left Column: Items List (Main Content) --- */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100 flex items-center gap-2 bg-slate-50/50">
              <Box size={18} className="text-primary"/>
              <h2 className="font-bold text-slate-700">اقلام سفارش ({order.items.length})</h2>
            </div>
            
            <div className="divide-y divide-slate-100">
              {order.items.map((item) => (
                <div key={item.id} className="p-5 hover:bg-slate-50 transition-colors">
                  <div className="flex flex-col sm:flex-row gap-4 justify-between items-start">
                    
                    {/* Item Info */}
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-lg text-slate-800">{item.product_name}</h3>
                        <span className="badge badge-ghost badge-sm">{item.quantity} عدد</span>
                      </div>
                      
                      {/* Specifications */}
                      <div className="text-sm text-slate-500 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
                        {item.specifications || 'بدون مشخصات خاص'}
                      </div>

                      {/* Download Files */}
                      {item.files && item.files.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {item.files.map((file) => (
                            <a 
                              key={file.id} 
                              href={file.file_url} 
                              target="_blank" 
                              rel="noreferrer"
                              className="btn btn-xs btn-outline btn-primary gap-1"
                            >
                              <Download size={12} />
                              دانلود {file.type_name}
                            </a>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Price */}
                    <div className="text-left min-w-[120px]">
                      <div className="font-bold text-lg text-emerald-600 dir-ltr">
                        {formatPrice(item.price)}
                      </div>
                      <span className="text-xs text-slate-400">IQD</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* --- Right Column: Customer & Payment Info (Sidebar) --- */}
        <div className="space-y-6">
          
          {/* Customer Info */}
          <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-slate-800 font-bold border-b border-slate-100 pb-3">
              <User size={18} className="text-primary"/>
              اطلاعات مشتری
            </div>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">نام کاربر:</span>
                <span className="font-medium">{order.user_info || 'نامشخص'}</span>
              </div>
              {/* اگر ایمیل یا موبایل هم در user_info بود اینجا پارس و نمایش میدیم */}
            </div>
          </div>

          {/* Shipping Address */}
          <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-slate-800 font-bold border-b border-slate-100 pb-3">
              <MapPin size={18} className="text-primary"/>
              آدرس ارسال
            </div>
            <p className="text-sm text-slate-600 leading-relaxed">
              {order.address_detail || 'آدرسی ثبت نشده است.'}
            </p>
          </div>

          {/* Payment Summary */}
          <div className="bg-slate-900 text-white p-6 rounded-2xl shadow-xl shadow-slate-900/20 space-y-4 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-secondary"></div>
            
            <div className="flex items-center gap-2 font-bold text-white/90 border-b border-white/10 pb-3">
              <CreditCard size={18}/>
              خلاصه مالی
            </div>
            
            <div className="space-y-2 text-sm text-white/70">
              <div className="flex justify-between">
                <span>تعداد اقلام:</span>
                <span>{order.items.length} ردیف</span>
              </div>
              <div className="flex justify-between">
                <span>مالیات / ارزش افزوده:</span>
                <span>0 IQD</span>
              </div>
            </div>

            <div className="pt-4 border-t border-white/10">
              <div className="flex justify-between items-end">
                <span className="text-sm font-medium text-white/80">مبلغ قابل پرداخت</span>
                <div className="text-2xl font-black text-emerald-400 dir-ltr">
                  {formatPrice(order.total_price)}
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default OrderDetailsPage;