import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, AlertTriangle, Clock } from 'lucide-react'; // این کلاک رو برای آیکون وضعیت آوردم
import { useAdminOrderDetails } from '../../hooks/useAdminOrderDetails';
import OrderHeader from './components/details/OrderHeader';
import OrderFinancials from './components/details/OrderFinancials';
import OrderItemsList from './components/details/OrderItemsList';
import OrderCustomerCard from './components/details/OrderCustomerCard';
import OrderInvoiceModule from './components/details/OrderInvoiceModule';

const OrderDetailsPage = () => {
  const navigate = useNavigate();
  const { order, isLoading, isError } = useAdminOrderDetails();

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center h-[60vh]">
      <span className="loading loading-spinner loading-lg text-primary"></span>
      <p className="mt-4 text-slate-400 font-medium">در حال بارگذاری جزئیات سفارش...</p>
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
    <div className="p-6 max-w-7xl mx-auto space-y-6 pb-24 animate-fade-in" dir="rtl">
      
      {/* بخش بالای صفحه: شامل دکمه بازگشت و وضعیت فعلی */}
      <div className="flex justify-between items-center mb-2">
        <a
          href='/admin/orders'
          className="btn btn-sm btn-ghost gap-2 text-slate-500 hover:text-slate-800"
        >
          <ArrowRight size={16} /> بازگشت به لیست سفارشات
        </a>

        {/* بج نمایش وضعیت فعلی سفارش */}
        <div className="flex items-center gap-2 bg-slate-100 text-slate-700 px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-bold">
          <Clock size={14} className="text-slate-500" />
          <span>وضعیت سفارش:</span>
          <span className="text-primary font-black">{order.current_status || "نامشخص"}</span>
        </div>
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
         <OrderHeader order={order} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* ستون راست: لیست اقلام */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm mb-4">
            <OrderItemsList order={order} />
          </div>

          <OrderInvoiceModule order={order}  />
        </div>

        {/* ستون چپ: اطلاعات مشتری و مالی */}
        <div className="space-y-6">
          
          {/* کارت اطلاعات مشتری */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
             <OrderCustomerCard order={order} />
          </div>

          {/* کارت مالی و تغییر قیمت */}
          <div className="rounded-2xl shadow-xl">
             <OrderFinancials order={order} />
          </div>

        </div>
      </div>
    </div>
  );
};

export default OrderDetailsPage;