import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowRight, User, MapPin, Calendar, CreditCard, 
  FileText, Download, Printer, Box, AlertTriangle 
} from 'lucide-react';
import { useAdminOrderDetails } from '../../hooks/useAdminOrderDetails';
import OrderStatusBadge from './components/OrderStatusBadge';
import { formatPrice } from '../../utils/formatPrice';

/**
 * کامپوننت کمکی برای نمایش مشخصات محصول
 */
const SpecificationDisplay = ({ specs }) => {
  if (!specs) return 'بدون مشخصات خاص';

  let data = specs;
  if (typeof specs === 'string') {
    try {
      data = JSON.parse(specs);
    } catch {
      return specs; 
    }
  }

  if (typeof data !== 'object' || data === null) {
    return <span>{String(data)}</span>;
  }

  const { width, height, has_design, options, ...rest } = data;

  return (
    <div className="flex flex-col gap-2 text-sm w-full">
      {(width || height) && (
        <div className="flex items-center gap-2">
          <span className="text-slate-400 text-xs font-medium">ابعاد:</span>
          <span className="font-bold text-slate-700 dir-ltr font-mono bg-slate-100 px-1.5 py-0.5 rounded text-xs">
            {width || '?'} × {height || '?'}
          </span>
        </div>
      )}

      {has_design !== undefined && (
        <div className="flex items-center gap-2">
          <span className="text-slate-400 text-xs font-medium">خدمات طراحی:</span>
          <span className={`badge badge-xs ${has_design ? 'badge-primary' : 'badge-ghost text-slate-400'}`}>
            {has_design ? 'دارد' : 'ندارد'}
          </span>
        </div>
      )}

      {options && typeof options === 'object' && Object.keys(options).length > 0 && (
        <div className="mt-1 bg-white border border-slate-200 rounded p-2">
          <span className="text-[10px] text-slate-400 font-bold block mb-1 uppercase tracking-wider">آپشن‌ها</span>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(options).map(([key, val]) => (
              <span key={key} className="inline-flex items-center px-2 py-1 rounded bg-slate-50 border border-slate-100 text-xs text-slate-600">
                <span className="font-medium ml-1">{key}:</span>
                <span className="text-slate-500">{String(val)}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {Object.entries(rest).map(([key, val]) => (
        <div key={key} className="flex gap-1 text-xs items-center">
          <span className="text-slate-400">{key}:</span>
          <span className="text-slate-600 truncate">{String(val)}</span>
        </div>
      ))}
    </div>
  );
};

// --- Helper برای نمایش نام کاربر ---
const renderUserInfo = (userInfo) => {
  if (!userInfo) return 'نامشخص';
  
  // اگر آبجکت است (مثل خطایی که داشتی: {id, username, full_name})
  if (typeof userInfo === 'object') {
    return userInfo.full_name || userInfo.username || `کاربر #${userInfo.id}`;
  }
  
  // اگر رشته است
  return userInfo;
};


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
    <div className="alert alert-error max-w-md mx-auto mt-10 shadow-lg">
      <AlertTriangle />
      <span>خطا در دریافت اطلاعات سفارش. لطفاً دوباره تلاش کنید.</span>
      <button onClick={() => navigate(-1)} className="btn btn-sm btn-ghost">بازگشت</button>
    </div>
  );

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 pb-20 animate-fade-in">
      
      {/* --- Header --- */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="btn btn-circle btn-ghost btn-sm text-slate-400 hover:text-slate-800 hover:bg-slate-100">
            <ArrowRight size={20} />
          </button>
          <div>
            <h1 className="text-2xl font-black text-slate-800 flex items-center gap-3">
              سفارش <span className="font-mono text-slate-400">#{order.id}</span>
              <OrderStatusBadge status={order.status_info} />
            </h1>
            <p className="text-slate-500 text-sm mt-1.5 flex items-center gap-2 font-medium">
              <Calendar size={14} className="text-slate-400"/>
              ثبت شده در {new Date(order.created_at).toLocaleDateString('fa-IR', { dateStyle: 'long' })} ساعت {new Date(order.created_at).toLocaleTimeString('fa-IR', {timeStyle: 'short'})}
            </p>
          </div>
        </div>
        
        <div className="flex gap-2 w-full md:w-auto">
          <button className="btn btn-outline gap-2 flex-1 md:flex-none hover:bg-slate-50 hover:text-slate-800 border-slate-200">
            <Printer size={18} />
            چاپ فاکتور
          </button>
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
                <div key={item.id} className="p-5 hover:bg-slate-50/50 transition-colors">
                  <div className="flex flex-col sm:flex-row gap-5 justify-between items-start">
                    
                    {/* Item Info */}
                    <div className="flex-1 space-y-3 w-full">
                      <div className="flex flex-wrap items-center gap-3">
                        <h3 className="font-bold text-lg text-slate-800">{item.product_name}</h3>
                        <span className="badge badge-ghost badge-sm border-slate-200 bg-white">{item.quantity} عدد</span>
                      </div>
                      
                      {/* Specifications Display Component */}
                      <div className="text-sm text-slate-500 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100 w-full">
                        <SpecificationDisplay specs={item.specifications} />
                      </div>

                      {/* Download Files */}
                      {item.files && item.files.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-dashed border-slate-200">
                          {item.files.map((file) => (
                            <a 
                              key={file.id} 
                              href={file.file_url} 
                              target="_blank" 
                              rel="noreferrer"
                              className="btn btn-xs btn-outline btn-primary gap-1.5 font-normal"
                            >
                              <Download size={12} />
                              دانلود {file.type_name}
                            </a>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Price */}
                    <div className="text-left min-w-[140px] pt-1">
                      <div className="font-black text-xl text-emerald-600 dir-ltr tracking-tight">
                        {formatPrice(item.price)}
                      </div>
                      <span className="text-xs text-slate-400 font-medium mt-1 block">دینار عراق (IQD)</span>
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
              <div className="flex justify-between items-center p-2 rounded hover:bg-slate-50 transition-colors">
                <span className="text-slate-500">نام کاربر:</span>
                {/* --- FIX: Handle Object vs String for User Info --- */}
                <span className="font-bold text-slate-700 dir-ltr">
                  {renderUserInfo(order.user_info)}
                </span>
              </div>
            </div>
          </div>

          {/* Shipping Address */}
          <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-slate-800 font-bold border-b border-slate-100 pb-3">
              <MapPin size={18} className="text-primary"/>
              آدرس ارسال
            </div>
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                <p className="text-sm text-slate-600 leading-relaxed">
                {order.address_detail || 'آدرسی ثبت نشده است.'}
                </p>
            </div>
          </div>

          {/* Payment Summary */}
          <div className="bg-slate-900 text-white p-6 rounded-2xl shadow-xl shadow-slate-900/20 space-y-5 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none group-hover:bg-primary/20 transition-all duration-500"></div>
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-secondary"></div>
            
            <div className="flex items-center gap-2 font-bold text-white/90 border-b border-white/10 pb-4 relative z-10">
              <CreditCard size={18}/>
              خلاصه مالی
            </div>
            
            <div className="space-y-3 text-sm text-white/70 relative z-10">
              <div className="flex justify-between">
                <span>تعداد اقلام:</span>
                <span className="text-white">{order.items.length} ردیف</span>
              </div>
              <div className="flex justify-between">
                <span>مالیات / ارزش افزوده:</span>
                <span className="text-white font-mono">0</span>
              </div>
            </div>

            <div className="pt-5 border-t border-white/10 relative z-10">
              <div className="flex justify-between items-end">
                <span className="text-sm font-medium text-white/80 mb-1">مبلغ قابل پرداخت</span>
                <div className="text-2xl font-black text-emerald-400 dir-ltr tracking-tight">
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