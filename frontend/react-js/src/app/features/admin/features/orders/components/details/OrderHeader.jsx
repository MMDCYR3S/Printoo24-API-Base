import React, { useState } from 'react';
import { Calendar, Printer, ChevronDown, RefreshCw } from 'lucide-react';
import { useAdminOrderDetails } from '../../../../hooks/useAdminOrderDetails';
import { useOrderStatuses } from '../../../../hooks/useOrderStatuses';
import OrderStatusBadge from '../OrderStatusBadge';

const OrderHeader = ({ order }) => {
  const { changeStatusMutation } = useAdminOrderDetails();
  const { statuses } = useOrderStatuses();
  
  const [modalOpen, setModalOpen] = useState(false);
  const [newStatusCode, setNewStatusCode] = useState('');
  const [description, setDescription] = useState('');

  const handleStatusSubmit = () => {
    if (!newStatusCode) return;
    changeStatusMutation.mutate(
      { status_code: newStatusCode, description },
      { onSuccess: () => {
        setModalOpen(false);
        setNewStatusCode('');
        setDescription('');
      }}
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
        
        {/* سمت راست: هویت سفارش */}
        <div className="flex items-center gap-5">
          <div className="p-4 bg-primary/10 rounded-2xl hidden sm:block">
            <RefreshCw size={32} className="text-primary" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-3xl font-black text-slate-800 tracking-tight">
                سفارش <span className="font-mono text-primary">#{order.id}</span>
              </h1>
              <div className="scale-110 origin-right mr-2">
                <OrderStatusBadge status={order.status_name} />
              </div>
            </div>
            <div className="flex items-center gap-4 text-slate-500 text-sm font-medium">
              <span className="flex items-center gap-1.5">
                <Calendar size={16} />
                {new Date(order.created_at).toLocaleDateString('fa-IR', { dateStyle: 'full' })}
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
              <span>ساعت {new Date(order.created_at).toLocaleTimeString('fa-IR', { timeStyle: 'short' })}</span>
            </div>
          </div>
        </div>
        
        {/* سمت چپ: اکشن‌های بزرگ و اصلی */}
        <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
          {/* دکمه چاپ با استایل ملایم‌تر */}
          <button className="btn btn-lg btn-outline border-slate-200 text-slate-600 hover:bg-slate-50 flex-1 lg:flex-none rounded-xl px-8">
            <Printer size={20} />
            چاپ فاکتور
          </button>

          {/* دکمه تغییر وضعیت: بزرگ، رنگی و بولد */}
          <button 
            onClick={() => setModalOpen(true)}
            className="btn btn-lg btn-primary flex-1 lg:flex-none rounded-xl px-10 shadow-lg shadow-primary/30 gap-2 text-white"
          >
            تغییر وضعیت سفارش
            <ChevronDown size={20} />
          </button>
        </div>
      </div>

      {/* مودال تغییر وضعیت با UI تمیزتر */}
      {modalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/60 backdrop-blur-md p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden border border-slate-100">
            <div className="bg-slate-50 p-6 border-b border-slate-100">
              <h3 className="text-xl font-black text-slate-800">بروزرسانی وضعیت سفارش</h3>
              <p className="text-sm text-slate-500 mt-1">وضعیت جدید را انتخاب کرده و در صورت نیاز توضیح اضافه کنید.</p>
            </div>
            
            <div className="p-8 space-y-6">
              <div className="form-control">
                <label className="label mb-1">
                  <span className="label-text font-bold text-slate-700">انتخاب وضعیت جدید</span>
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {statuses?.map(s => (
                    <button
                      key={s.id}
                      type="button"
                      onClick={() => setNewStatusCode(s.internal_code)}
                      className={`btn btn-md rounded-xl transition-all ${
                        newStatusCode === s.internal_code 
                        ? 'btn-primary text-white shadow-md' 
                        : 'btn-outline border-slate-200 text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      {s.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* <div className="form-control">
                <label className="label mb-1">
                  <span className="label-text font-bold text-slate-700">توضیحات داخلی (لاگ سیستم)</span>
                </label>
                <textarea 
                  className="textarea textarea-bordered h-28 bg-slate-50 focus:bg-white focus:border-primary rounded-xl text-base" 
                  placeholder="دلیل تغییر وضعیت یا نکته‌ای برای ادمین‌های دیگر..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                ></textarea>
              </div> */}

              <div className="flex gap-4 pt-4">
                <button 
                  onClick={() => setModalOpen(false)} 
                  className="btn btn-lg flex-1 btn-ghost rounded-xl"
                  disabled={changeStatusMutation.isPending}
                >
                  انصراف
                </button>
                <button 
                  onClick={handleStatusSubmit} 
                  className="btn btn-lg flex-1 btn-primary rounded-xl text-white"
                  disabled={!newStatusCode || changeStatusMutation.isPending}
                >
                  {changeStatusMutation.isPending ? <span className="loading loading-spinner"></span> : 'تایید و ثبت نهایی'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderHeader;