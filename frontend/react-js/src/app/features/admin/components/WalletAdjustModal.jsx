import React from 'react';
import { useForm } from 'react-hook-form';
import { X, Wallet, ArrowUpCircle, ArrowDownCircle } from 'lucide-react'; // FileText حذف شد چون توضیحات نداریم
import { useAdminWallets } from '../hooks/useAdminWallets';

const WalletAdjustModal = ({ isOpen, onClose, user }) => {
  const { adjustBalanceMutation } = useAdminWallets();
  
  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm({
    defaultValues: {
      action_type: 'deposit',
      amount: '',
      // description حذف شد
    }
  });

  const actionType = watch('action_type');

  const onSubmit = (data) => {
    // اصلاحات مهم برای رفع خطا:
    // 1. تبدیل user.id به عدد (Integer) محض احتیاط
    // 2. حذف description چون در سواگر نبود
    // 3. ارسال amount به صورت رشته (طبق مثال سواگر "100000.00")
    
    const payload = {
      user_id: Number(user.id), 
      amount: data.amount.toString(),
      action_type: data.action_type
    };

    // لاگ برای دیباگ کردن (تو کنسول مرورگر چک کن چی ارسال میشه)
    console.log("Sending Payload:", payload);

    adjustBalanceMutation.mutate(payload, {
      onSuccess: () => {
        reset();
        onClose();
      }
    });
  };

  if (!isOpen || !user) return null;

  return (
    <dialog className="modal modal-open backdrop-blur-md bg-slate-900/60 z-[60] animate-in fade-in duration-200">
      <div className="modal-box w-full max-w-md rounded-[2rem] p-0 overflow-hidden shadow-2xl bg-white ring-1 ring-white/50">
        
        {/* Header */}
        <div className="bg-slate-50/80 backdrop-blur border-b border-slate-100 p-4 flex justify-between items-center sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white rounded-full shadow-sm border border-slate-100 flex items-center justify-center text-emerald-600">
              <Wallet size={20} />
            </div>
            <div>
              <h3 className="font-bold text-slate-800">مدیریت کیف پول</h3>
              <p className="text-xs text-slate-500 font-mono mt-0.5 tracking-wide">@{user.username}</p>
            </div>
          </div>
          <button onClick={onClose} className="btn btn-circle btn-ghost btn-sm text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Current Balance */}
        <div className="relative py-8 bg-gradient-to-b from-slate-50 to-white flex flex-col items-center justify-center border-b border-slate-100 border-dashed">
            <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold mb-1">موجودی فعلی</span>
            <div className="flex items-baseline gap-1 dir-ltr">
                <span className={`text-4xl font-black font-mono tracking-tighter ${Number(user.wallet_balance) < 0 ? 'text-red-600' : 'text-slate-800'}`}>
                    {Number(user.wallet_balance || 0).toLocaleString()}
                </span>
                <span className="text-sm font-bold text-slate-400">IQD</span>
            </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-5 bg-white">
          
          {/* Action Selector */}
          <div className="grid grid-cols-2 gap-3 p-1.5 bg-slate-100/80 rounded-2xl">
            <label className={`flex flex-col items-center justify-center gap-1.5 py-3 rounded-xl cursor-pointer transition-all duration-200 border-2 ${actionType === 'deposit' ? 'bg-white border-emerald-500 shadow-sm text-emerald-700' : 'border-transparent text-slate-400 hover:bg-slate-200/50 hover:text-slate-600'}`}>
              <input type="radio" value="deposit" className="hidden" {...register('action_type')} />
              <ArrowDownCircle size={24} className={actionType === 'deposit' ? 'animate-bounce-slow' : ''} />
              <span className="text-xs font-bold">واریز (شارژ)</span>
            </label>
            
            <label className={`flex flex-col items-center justify-center gap-1.5 py-3 rounded-xl cursor-pointer transition-all duration-200 border-2 ${actionType === 'debit' ? 'bg-white border-red-500 shadow-sm text-red-700' : 'border-transparent text-slate-400 hover:bg-slate-200/50 hover:text-slate-600'}`}>
              <input type="radio" value="debit" className="hidden" {...register('action_type')} />
              <ArrowUpCircle size={24} className={actionType === 'debit' ? 'animate-bounce-slow' : ''} />
              <span className="text-xs font-bold">برداشت (کسر)</span>
            </label>
          </div>

          {/* Amount Input */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-500 mr-1">مبلغ تراکنش</label>
            <div className="relative group">
                <input 
                  type="number" 
                  {...register('amount', { required: 'لطفا مبلغ را وارد کنید', min: { value: 100, message: 'حداقل مبلغ ۱۰۰ دینار است' } })}
                  className="input input-lg w-full bg-slate-50 border-slate-200 focus:bg-white focus:border-primary focus:ring-4 focus:ring-primary/10 rounded-2xl font-mono text-xl pl-16 transition-all" 
                  placeholder="0"
                />
                <span className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400 text-sm font-bold pointer-events-none">IQD</span>
            </div>
            {errors.amount && <span className="text-red-500 text-[10px] font-medium mr-1 animate-pulse">{errors.amount.message}</span>}
          </div>

          {/* Description Removed - فیلد توضیحات حذف شد چون در API ساپورت نمی‌شد */}

          {/* Submit Button */}
          <button 
            type="submit" 
            disabled={adjustBalanceMutation.isPending}
            className={`btn btn-lg w-full rounded-2xl text-white shadow-xl shadow-current/20 gap-3 border-0 mt-2 ${actionType === 'deposit' ? 'bg-emerald-500 hover:bg-emerald-600' : 'bg-red-500 hover:bg-red-600'}`}
          >
            {adjustBalanceMutation.isPending ? <span className="loading loading-dots loading-md"/> : (
               actionType === 'deposit' ? <ArrowDownCircle size={22} /> : <ArrowUpCircle size={22} />
            )}
            {actionType === 'deposit' ? 'افزایش موجودی کیف پول' : 'کسر از موجودی کیف پول'}
          </button>

        </form>
      </div>
    </dialog>
  );
};

export default WalletAdjustModal;