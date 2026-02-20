import React, { useState } from 'react';
import { CreditCard, Edit, Check, X } from 'lucide-react';
import { useAdminOrderDetails } from '../../../../hooks/useAdminOrderDetails';
import { formatPrice } from '../../../../utils/formatPrice';

const OrderFinancials = ({ order }) => {
  const { updateOrderMutation } = useAdminOrderDetails();
  
  const [isEditingPrice, setIsEditingPrice] = useState(false);
  const [customPrice, setCustomPrice] = useState(order.total_price || '');

  const handleUpdatePrice = () => {
    if (!customPrice) return;
    
    updateOrderMutation.mutate(
      { total_price: parseFloat(customPrice) },
      { 
        onSuccess: () => setIsEditingPrice(false) 
      }
    );
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden flex flex-col h-full">
      {/* هدر بخش مالی */}
      <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center gap-3">
        <div className="p-2 bg-white rounded-lg shadow-sm border border-slate-100 text-primary">
          <CreditCard size={18} />
        </div>
        <h3 className="font-bold text-slate-800 text-lg">خلاصه مالی سفارش</h3>
      </div>
      
      {/* محتوای اصلی */}
      <div className="p-6 flex flex-col flex-1">
        <div className="space-y-4 mb-6">
          <div className="flex justify-between items-center pb-3 border-b border-slate-100">
            <span className="text-sm font-medium text-slate-500">تعداد اقلام:</span>
            <span className="text-sm font-bold text-slate-800 bg-slate-100 px-3 py-1 rounded-md">
              {order.items_count || order.items?.length || 0} ردیف
            </span>
          </div>
          
          <div className="flex justify-between items-center pb-3 border-b border-slate-100">
            <span className="text-sm font-medium text-slate-500">وضعیت پرداخت:</span>
            {/* می‌تونی رنگ این بج رو بر اساس وضعیت داینامیک کنی. فعلا زرد/نارنجی گذاشتم */}
            <span className="text-xs font-bold text-amber-700 bg-amber-50 border border-amber-200 px-2.5 py-1 rounded-md">
              بررسی نشده
            </span>
          </div>
        </div>

        {/* باکس مبلغ کل و ویرایش (پایین کارت می‌شینه) */}
        <div className="mt-auto">
          <div className="bg-emerald-50/70 border border-emerald-100 rounded-xl p-5">
            <div className="flex justify-between items-center mb-4">
              <span className="text-sm font-bold text-emerald-800">مبلغ کل قابل پرداخت</span>
              
              {!isEditingPrice && (
                <button 
                  onClick={() => setIsEditingPrice(true)}
                  className="flex items-center gap-1.5 text-xs font-bold text-emerald-600 hover:text-emerald-800 hover:bg-emerald-100 px-2.5 py-1.5 rounded-md transition-colors"
                >
                  <Edit size={14}/> ویرایش دستی
                </button>
              )}
            </div>

            {isEditingPrice ? (
              <div className="flex flex-col gap-3 animate-in fade-in duration-200">
                <div className="relative">
                  <input 
                    type="number" 
                    className="w-full bg-white border border-emerald-200 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 rounded-lg px-4 py-2.5 text-left dir-ltr font-mono text-emerald-800 font-bold placeholder-emerald-300 outline-none transition-all"
                    value={customPrice}
                    onChange={(e) => setCustomPrice(e.target.value)}
                    placeholder="مبلغ جدید (IQD)"
                  />
                  <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-bold text-emerald-400">IQD</span>
                </div>
                
                <div className="flex gap-2">
                  <button 
                    onClick={handleUpdatePrice} 
                    className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-sm py-2 rounded-lg flex items-center justify-center gap-1.5 transition-colors shadow-sm" 
                    disabled={updateOrderMutation.isPending}
                  >
                    {updateOrderMutation.isPending ? (
                      <span className="loading loading-spinner loading-sm"></span>
                    ) : (
                      <><Check size={16}/> تایید</>
                    )}
                  </button>
                  <button 
                    onClick={() => { setIsEditingPrice(false); setCustomPrice(order.total_price); }} 
                    className="flex-1 bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 font-bold text-sm py-2 rounded-lg flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <X size={16}/> انصراف
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-3xl font-black text-emerald-600 dir-ltr tracking-tight text-left">
                {formatPrice(order.total_price)} <span className="text-sm font-bold text-emerald-600/60 ml-1">IQD</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderFinancials;