import React, { useState, useEffect } from 'react';
import { 
  FileCheck, ShieldCheck, Trash2, Edit3, Plus, AlertCircle, 
  DollarSign, Calculator, Calendar, Tag, ArrowLeftRight, Clock, X 
} from 'lucide-react';
import { useAdminInvoices } from '../../../../hooks/useAdminInvoices';
import { formatPrice } from '../../../../utils/formatPrice';

const OrderInvoiceModule = ({ order }) => {
  const { 
    invoice, 
    isLoading, 
    createMutation, 
    updateMutation, 
    approveMutation, 
    deleteMutation, 
    changeStatusMutation 
  } = useAdminInvoices(order.id);

  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({});

  // سینک کردن استیت فرم با دیتای اینویس هنگام باز شدن مودال
  useEffect(() => {
    if (invoice && isEditing) {
      setFormData({
        paid_amount: invoice.paid_amount,
        items_amount: invoice.items_amount,
        services_amount: invoice.services_amount,
        tax_amount: invoice.tax_amount,
        discount_amount: invoice.discount_amount,
        final_amount: invoice.final_amount,
        description: invoice.description,
        due_date: invoice.due_date,
        status: invoice.status
      });
    }
  }, [invoice, isEditing]);

  if (isLoading) return <div className="flex justify-center p-12"><span className="loading loading-spinner text-primary"></span></div>;

  // --- اگر فاکتور وجود ندارد ---
  if (!invoice) {
    return (
      <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-xl p-10 text-center">
        <div className="bg-white w-14 h-14 rounded-full flex items-center justify-center mx-auto shadow-sm text-slate-300 mb-4">
          <Plus size={28} />
        </div>
        <h3 className="text-lg font-bold text-slate-700">صدور فاکتور مالی</h3>
        <p className="text-slate-500 text-xs mb-6 max-w-xs mx-auto">هنوز فاکتوری برای این سفارش صادر نشده است.</p>
        <button 
          onClick={() => createMutation.mutate({ 
            order_id: order.id, 
            final_amount: order.total_price, 
            items_amount: order.total_price,
            status: 'PENDING' 
          })}
          className="btn btn-primary rounded-xl px-8 shadow-lg shadow-primary/20"
        >
          ایجاد فاکتور اولیه
        </button>
      </div>
    );
  }

  const isFinalized = invoice.status === 'FINALIZE';
  const remaining = (parseFloat(invoice.final_amount) || 0) - (parseFloat(invoice.paid_amount) || 0);

  const getStatusBadge = (status) => {
    const styles = {
      'PENDING': 'bg-amber-100 text-amber-700 border-amber-200',
      'PAID_PARTIAL': 'bg-blue-100 text-blue-700 border-blue-200',
      'PAID_FULL': 'bg-emerald-100 text-emerald-700 border-emerald-200',
      'CANCELED': 'bg-red-100 text-red-700 border-red-200',
      'FINALIZE': 'bg-slate-800 text-white border-slate-700'
    };
    return styles[status] || 'bg-slate-100 text-slate-600 border-slate-200';
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden transition-all">
      
      {/* هدر ماژول */}
      <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex flex-wrap justify-between items-center gap-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${isFinalized ? 'bg-slate-800' : 'bg-primary'} text-white shadow-sm`}>
            <FileCheck size={20} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-slate-800 text-sm">مدیریت فاکتور مالی</h3>
              <span className={`text-[10px] font-black px-2 py-0.5 rounded border uppercase ${getStatusBadge(invoice.status)}`}>
                {invoice.status}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {!isFinalized && (
            <>
              {/* تغییر وضعیت دستی */}
              <select 
                className="select select-bordered select-xs h-8 rounded-lg text-[10px] font-bold bg-white"
                value={invoice.status}
                onChange={(e) => changeStatusMutation.mutate({ id: invoice.id, status: e.target.value })}
                disabled={changeStatusMutation.isPending}
              >
                <option value="PENDING">وضعیت: در انتظار</option>
                <option value="PAID_PARTIAL">وضعیت: پرداخت ناقص</option>
                <option value="PAID_FULL">وضعیت: تسویه کامل</option>
                <option value="CANCELED">وضعیت: لغو شده</option>
              </select>

              <button 
                onClick={() => approveMutation.mutate(invoice.id)} 
                className="btn btn-xs h-8 btn-success text-white px-3 rounded-lg font-bold"
                disabled={approveMutation.isPending}
              >
                نهایی‌سازی (Lock)
              </button>
              
              <button 
                onClick={() => {if(window.confirm('فاکتور حذف شود؟')) deleteMutation.mutate(invoice.id)}} 
                className="btn btn-xs h-8 btn-ghost text-slate-400 hover:text-error rounded-lg"
              >
                <Trash2 size={14} />
              </button>
            </>
          )}
          {isFinalized && (
            <div className="flex items-center gap-1.5 text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-100 text-[11px] font-black">
              <ShieldCheck size={16}/> فاکتور نهایی شده
            </div>
          )}
        </div>
      </div>

      <div className="p-6">
        {/* مبالغ کلیدی */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="flex items-center gap-1.5 text-[10px] font-bold text-slate-400 mb-1"><Calculator size={12}/> مبلغ اقلام</span>
            <div className="text-sm font-black text-slate-700 dir-ltr text-right">{formatPrice(invoice.items_amount || 0)}</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="flex items-center gap-1.5 text-[10px] font-bold text-slate-400 mb-1"><Plus size={12}/> خدمات و مالیات</span>
            <div className="text-sm font-black text-slate-700 dir-ltr text-right">{formatPrice((parseFloat(invoice.services_amount)||0) + (parseFloat(invoice.tax_amount)||0))}</div>
          </div>
          <div className="p-3 bg-red-50/50 rounded-lg border border-red-100">
            <span className="flex items-center gap-1.5 text-[10px] font-bold text-red-400 mb-1"><Tag size={12}/> تخفیف</span>
            <div className="text-sm font-black text-red-600 dir-ltr text-right">{formatPrice(invoice.discount_amount || 0)}-</div>
          </div>
          <div className="p-3 bg-primary/5 rounded-lg border border-primary/10">
            <span className="flex items-center gap-1.5 text-[10px] font-bold text-primary mb-1"><DollarSign size={12}/> مبلغ کل فاکتور</span>
            <div className="text-sm font-black text-primary dir-ltr text-right">{formatPrice(invoice.final_amount)}</div>
          </div>
        </div>

        {/* وضعیت پرداخت و مانده */}
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1 bg-emerald-50/40 border border-emerald-100 rounded-xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-500 rounded-lg flex items-center justify-center text-white shadow-sm"><ArrowLeftRight size={20}/></div>
              <div>
                <p className="text-[10px] font-bold text-emerald-700/60 uppercase">جمع دریافتی</p>
                <p className="text-lg font-black text-emerald-600 dir-ltr">{formatPrice(invoice.paid_amount || 0)}</p>
              </div>
            </div>
            {!isFinalized && (
              <button onClick={() => setIsEditing(true)} className="p-2 hover:bg-emerald-100 rounded-lg text-emerald-600 transition-colors">
                <Edit3 size={18}/>
              </button>
            )}
          </div>

          <div className={`flex-1 rounded-xl p-4 border flex items-center gap-3 ${remaining > 0 ? 'bg-orange-50 border-orange-100' : 'bg-slate-50 border-slate-200'}`}>
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white ${remaining > 0 ? 'bg-orange-500 shadow-md shadow-orange-200' : 'bg-slate-400'}`}>
              <Clock size={20}/>
            </div>
            <div>
              <p className={`text-[10px] font-bold ${remaining > 0 ? 'text-orange-700/60' : 'text-slate-400'} uppercase`}>مانده بدهی</p>
              <p className={`text-lg font-black dir-ltr ${remaining > 0 ? 'text-orange-600' : 'text-slate-500'}`}>{formatPrice(remaining)}</p>
            </div>
          </div>
        </div>

        {/* فوتر اطلاعات */}
        <div className="mt-6 flex flex-wrap items-center gap-6 text-[10px] font-bold text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-100">
          <div className="flex items-center gap-1.5">
            <Calendar size={14} className="text-slate-400"/>
            سررسید: <span className="text-slate-800">{invoice.due_date ? new Date(invoice.due_date).toLocaleDateString('EN') : 'ثبت نشده'}</span>
          </div>
          {invoice.description && (
            <div className="flex items-start gap-1.5 flex-1 border-r border-slate-200 pr-6">
              <AlertCircle size={14} className="text-slate-400 shrink-0"/>
              <span className="line-clamp-1 italic text-slate-400">{invoice.description}</span>
            </div>
          )}
        </div>
      </div>

      {/* مودال ویرایش تمام فیلدها */}
      {isEditing && (
        <div className="fixed inset-0 z-[150] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-xl overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
              <h3 className="font-bold text-slate-800">ویرایش جزئیات فاکتور #{invoice.id}</h3>
              <button onClick={() => setIsEditing(false)} className="text-slate-400 hover:text-slate-600"><X size={20}/></button>
            </div>
            
            <div className="p-6 grid grid-cols-2 gap-x-6 gap-y-4">
              {[
                { label: 'مبلغ اقلام', key: 'items_amount' },
                { label: 'هزینه خدمات', key: 'services_amount' },
                { label: 'مالیات', key: 'tax_amount' },
                { label: 'تخفیف', key: 'discount_amount' },
                { label: 'مبلغ نهایی (قابل پرداخت)', key: 'final_amount' },
                { label: 'مبلغ دریافتی (Paid)', key: 'paid_amount' },
              ].map((f) => (
                <div key={f.key} className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-500 uppercase">{f.label}</label>
                  <input 
                    type="number" 
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm font-mono focus:border-primary outline-none transition-all"
                    value={formData[f.key] || 0}
                    onChange={(e) => setFormData({...formData, [f.key]: e.target.value})}
                  />
                </div>
              ))}
              
              <div className="col-span-2 space-y-1 mt-2">
                <label className="text-[11px] font-bold text-slate-500 uppercase">تاریخ سررسید تسویه (ISO Format)</label>
                <input 
                  type="text" 
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm font-mono"
                  placeholder="2026-08-15T10:00:00Z"
                  value={formData.due_date || ''}
                  onChange={(e) => setFormData({...formData, due_date: e.target.value})}
                />
              </div>

              <div className="col-span-2 space-y-1">
                <label className="text-[11px] font-bold text-slate-500 uppercase">توضیحات و یادداشت مالی</label>
                <textarea 
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm min-h-[80px] outline-none focus:border-primary"
                  value={formData.description || ''}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                />
              </div>
            </div>

            <div className="p-4 bg-slate-50 border-t border-slate-200 flex gap-3">
              <button onClick={() => setIsEditing(false)} className="btn btn-ghost flex-1 font-bold">انصراف</button>
              <button 
                onClick={() => updateMutation.mutate(
                  { id: invoice.id, data: formData }, 
                  { onSuccess: () => setIsEditing(false) }
                )}
                className="btn btn-primary flex-[2] text-white font-black"
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? 'در حال ثبت...' : 'ذخیره تغییرات مالی'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderInvoiceModule;