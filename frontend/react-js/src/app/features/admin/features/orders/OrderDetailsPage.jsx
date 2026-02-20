import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, AlertTriangle } from 'lucide-react';
import { useAdminOrderDetails } from '../../hooks/useAdminOrderDetails';
import OrderHeader from './components/details/OrderHeader';
import OrderFinancials from './components/details/OrderFinancials';
import OrderItemsList from './components/details/OrderItemsList';
import OrderCustomerCard from './components/details/OrderCustomerCard';
import OrderInvoiceModule from './components/details/OrderInvoiceModule';

// این کامپوننت‌ها رو تو قدم‌های بعدی یکی یکی با هم می‌سازیم
// import OrderHeader from './components/details/OrderHeader';
// import OrderItemsList from './components/details/OrderItemsList';
// import OrderCustomerCard from './components/details/OrderCustomerCard';
// import OrderFinancials from './components/details/OrderFinancials';

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
    <div className="p-6 max-w-7xl mx-auto space-y-6 pb-24 animate-fade-in">
      
      {/* دکمه بازگشت */}
      <button 
        onClick={() => navigate(-1)} 
        className="btn btn-sm btn-ghost gap-2 text-slate-500 hover:text-slate-800 mb-2"
      >
        <ArrowRight size={16} /> بازگشت به لیست سفارشات
      </button>

<div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
         <OrderHeader order={order} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* ستون راست: لیست اقلام */}
<div className="lg:col-span-2">
  <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 mb-4">
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
<div className=" rounded-2xl shadow-xl">
             <OrderFinancials order={order} />
          </div>

        </div>
      </div>
    </div>
  );
};

export default OrderDetailsPage;