import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ArrowRight, Edit, Package, Layers, DollarSign, Image as ImageIcon, 
  CheckCircle2, XCircle, Calculator, AlertCircle, Paperclip, CheckSquare, 
  List, Link2, Download, ShieldAlert, Check
} from 'lucide-react';
import clsx from 'clsx';
import { adminProductService } from '../../services/adminProductService';

const formatPrice = (price) => {
    if (!price || isNaN(price)) return "0";
    return new Intl.NumberFormat('fa-IR').format(Number(price));
};

const ProductDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeImage, setActiveImage] = useState(0);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin-product', id],
    queryFn: () => adminProductService.getById(id),
    staleTime: 0,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 relative overflow-hidden">
        <div className="absolute w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[100px] animate-pulse"></div>
        <div className="relative z-10 flex flex-col items-center gap-6 bg-white/50 backdrop-blur-xl p-10 rounded-[3rem] shadow-2xl shadow-slate-200/50 border border-white">
          <span className="loading loading-spinner loading-lg text-primary mb-2"></span>
          <div className="flex flex-col items-center gap-1">
            <span className="font-black text-xl text-slate-800">در حال دریافت اطلاعات محصول</span>
            <span className="text-slate-500 text-sm font-medium">لطفاً چند لحظه صبر کنید...</span>
          </div>
        </div>
      </div>
    );
  }

  if (isError || !data || !data.shell) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 relative overflow-hidden">
        <div className="relative z-10 flex flex-col items-center gap-6 bg-white/70 backdrop-blur-xl p-10 rounded-[3rem] shadow-2xl shadow-red-500/10 border border-red-50 text-center max-w-sm">
          <ShieldAlert size={48} className="text-red-500"/>
          <h2 className="text-2xl font-black text-slate-800">محصول یافت نشد!</h2>
          <button onClick={() => navigate('/admin/products')} className="btn btn-error text-white rounded-full w-full shadow-lg shadow-red-500/30">
            بازگشت به لیست محصولات
          </button>
        </div>
      </div>
    );
  }

  // === استخراج داده‌ها با بالاترین سطح امنیت ===
  const shell = data?.shell || {};
  const fields = Array.isArray(data?.fields) ? data.fields : [];
  const formulas = Array.isArray(data?.formulas) ? data.formulas : [];
  const images = Array.isArray(data?.images) ? data.images : [];
  const attachments = Array.isArray(data?.attachments) ? data.attachments : [];

  // تنظیم نام دسته‌بندی
  let categoryDisplay = 'بدون دسته‌بندی';
  if (shell?.category_info && typeof shell?.category_info === 'object') {
     const pName = shell?.category_info?.parent_name;
     const cName = shell?.category_info?.name;
     if (pName && cName) categoryDisplay = `${pName} > ${cName}`;
     else if (cName) categoryDisplay = cName;
     else if (pName) categoryDisplay = pName;
  } else if (typeof shell?.category_info === 'string') {
     categoryDisplay = shell?.category_info;
  } else if (typeof shell?.category === 'string') {
     categoryDisplay = shell?.category;
  }

  // تابع شروط 
  const getConditionText = (cond) => {
      if (!cond) return "شرط نامعتبر";
      const targetField = fields.find(f => f?.id === cond?.trigger_field_id);
      const targetChoice = targetField?.choices?.find(c => c?.id === cond?.trigger_choice_id);
      const actionText = { 'show': 'آشکار', 'hide': 'پنهان', 'enable': 'فعال', 'disable': 'غیرفعال' }[cond?.action] || cond?.action || 'نامشخص';
      const opText = { 'equals': 'برابر با', 'not_equals': 'مخالف', 'is_empty': 'خالی', 'is_not_empty': 'پر' }[cond?.operator] || cond?.operator || 'باشد';
      
      if (!targetField) return "فیلد وابسته حذف شده است";
      return `${actionText} می‌شود اگر [${targetField?.title || 'بدون نام'}] ${opText} ${targetChoice ? `[${targetChoice?.title || 'گزینه'}]` : ''}`;
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] pb-32 font-sans selection:bg-blue-500/20">
      
      {/* Header */}
      <div className="sticky top-0 z-40 bg-white/70 backdrop-blur-2xl border-b border-white shadow-[0_4px_30px_rgba(0,0,0,0.03)] px-6 py-4 flex justify-between items-center transition-all">
        <div className="flex items-center gap-5">
          <button onClick={() => navigate('/admin/products')} className="w-10 h-10 flex items-center justify-center bg-white border border-slate-200 text-slate-600 rounded-full shadow-sm hover:bg-slate-50 hover:text-blue-600 transition-all active:scale-95">
            <ArrowRight size={20} />
          </button>
          <div className="flex flex-col">
            <h1 className="text-xl font-black text-slate-800 tracking-tight flex items-center gap-3">
               جزئیات محصول
               {shell?.is_active ? (
                  <span className="badge badge-success badge-sm text-white gap-1"><CheckCircle2 size={12}/> فعال</span>
               ) : (
                  <span className="badge badge-error badge-sm text-white gap-1"><XCircle size={12}/> غیرفعال</span>
               )}
            </h1>
            <span className="text-[11px] text-slate-400 font-bold mt-0.5 font-mono">{shell?.code || '---'} | ID: {shell?.id || '---'}</span>
          </div>
        </div>
        
        <Link to={`/admin/products/edit/${shell?.id || ''}`} className="btn btn-primary btn-sm h-10 px-6 rounded-full shadow-lg shadow-primary/30 gap-2 hover:scale-105 transition-transform">
           <Edit size={16}/> ویرایش محصول
        </Link>
      </div>

      <div className="max-w-7xl mx-auto mt-10 px-6 space-y-8">
        
        {/* ROW 1: Basic Info & Gallery */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
           
           {/* Gallery */}
           <div className="lg:col-span-4 space-y-4">
              <div className="bg-white p-2 rounded-[2rem] shadow-xl shadow-slate-200/50 border border-white aspect-square relative overflow-hidden">
                 {images[activeImage]?.image ? (
                    <img src={images[activeImage]?.image} alt={shell?.name || 'تصویر'} className="w-full h-full object-cover rounded-[1.5rem]" />
                 ) : (
                    <div className="w-full h-full bg-slate-50 rounded-[1.5rem] flex flex-col items-center justify-center text-slate-300 gap-3">
                       <ImageIcon size={48} strokeWidth={1} />
                       <span className="text-sm font-bold">بدون تصویر</span>
                    </div>
                 )}
              </div>
              
              {images.length > 1 && (
                 <div className="flex gap-3 overflow-x-auto pb-2 custom-scrollbar">
                    {images.map((img, idx) => (
                       <button 
                          key={img?.id || idx} 
                          onClick={() => setActiveImage(idx)}
                          className={clsx(
                             "w-20 h-20 flex-shrink-0 rounded-2xl overflow-hidden border-2 transition-all",
                             activeImage === idx ? "border-primary shadow-md scale-105" : "border-transparent opacity-70 hover:opacity-100"
                          )}
                       >
                          {img?.image && <img src={img?.image} alt="" className="w-full h-full object-cover" />}
                       </button>
                    ))}
                 </div>
              )}
           </div>

           {/* Info Cards */}
           <div className="lg:col-span-8 flex flex-col gap-6">
              <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 rounded-[2rem] flex-1">
                 <div className="flex items-start gap-4 mb-6">
                    <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                       <Package size={28} />
                    </div>
                    <div>
                       <h2 className="text-2xl font-black text-slate-800">{shell?.name || 'بدون نام'}</h2>
                       <div className="flex items-center gap-2 mt-2 text-sm font-bold text-slate-500">
                          <Layers size={16}/> 
                          {categoryDisplay}
                       </div>
                    </div>
                 </div>

                 <div className="bg-slate-50/50 p-5 rounded-2xl border border-slate-100 text-sm text-slate-600 leading-relaxed font-medium mb-6">
                    {shell?.description || <span className="italic opacity-50">توضیحاتی ثبت نشده است.</span>}
                 </div>

                 <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {/* Price Card */}
                    <div className="bg-gradient-to-br from-emerald-50 to-emerald-100/50 p-5 rounded-2xl border border-emerald-100">
                       <div className="flex items-center gap-2 text-emerald-700 font-black mb-3">
                          <DollarSign size={18}/> اطلاعات مالی
                       </div>
                       {shell?.has_price ? (
                          <div className="space-y-3">
                             <div className="flex justify-between items-center text-sm">
                                <span className="text-emerald-800/70 font-bold">قیمت نمایشی:</span>
                                <span className="font-black text-emerald-700 dir-ltr flex items-center gap-1">
                                   {formatPrice(shell?.show_price)} <span className="text-[10px] opacity-70">IQD</span>
                                </span>
                             </div>
                             <div className="flex justify-between items-center text-sm border-t border-emerald-200/50 pt-3">
                                <span className="text-emerald-800/70 font-bold">قیمت پایه سیستم:</span>
                                <span className="font-black text-emerald-700 dir-ltr flex items-center gap-1">
                                   {formatPrice(shell?.price_per_unit)} <span className="text-[10px] opacity-70">IQD</span>
                                </span>
                             </div>
                          </div>
                       ) : (
                          <div className="text-sm font-bold text-amber-600 bg-amber-50 p-2 rounded-xl text-center border border-amber-200/50">
                             محصول استعلامی (بدون قیمت)
                          </div>
                       )}
                    </div>

                    {/* Guide Card */}
                    <div className={clsx("p-5 rounded-2xl border flex flex-col", 
                       shell?.guide_type === 'warning' ? "bg-amber-50 border-amber-100 text-amber-800" :
                       shell?.guide_type === 'tip' ? "bg-purple-50 border-purple-100 text-purple-800" :
                       "bg-blue-50 border-blue-100 text-blue-800"
                    )}>
                       <div className="flex items-center gap-2 font-black mb-3">
                          <AlertCircle size={18}/> پیام راهنما
                       </div>
                       <p className="text-sm font-medium leading-relaxed opacity-90 flex-1">
                          {shell?.guide_text || "پیامی ثبت نشده است."}
                       </p>
                       <div className="mt-3 text-xs font-bold opacity-60 flex items-center gap-1">
                          <CheckSquare size={14}/>
                          {shell?.has_quantity ? "مشتری می‌تواند تعداد دلخواه وارد کند" : "انتخاب تعداد از روی گزینه‌های فرم"}
                       </div>
                    </div>
                 </div>
              </div>
           </div>
        </div>

        {/* ROW 2: Form Builder Fields */}
        <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 rounded-[2rem]">
           <div className="flex items-center gap-4 mb-8 pb-4 border-b border-slate-100">
              <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
                 <List size={24} />
              </div>
              <div>
                 <h3 className="text-xl font-black text-slate-800">ساختار فرم (ویژگی‌ها)</h3>
                 <p className="text-sm text-slate-500 font-medium mt-1">فیلدهایی که در صفحه محصول به مشتری نمایش داده می‌شود</p>
              </div>
           </div>

           {fields.length === 0 ? (
              <div className="text-center py-10 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200 text-slate-400 font-bold">
                 هیچ فیلدی برای این محصول تعریف نشده است.
              </div>
           ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                 {fields.map((field, idx) => (
                    <div key={field?.id || idx} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
                       <div className="absolute top-0 right-0 w-1 h-full bg-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                       
                       <div className="flex justify-between items-start mb-4">
                          <div>
                             <h4 className="font-black text-slate-800 text-lg flex items-center gap-2">
                                {field?.title || 'بدون عنوان'}
                                {field?.is_required && <span className="text-[10px] bg-red-50 text-red-500 px-2 py-0.5 rounded-md">اجباری</span>}
                             </h4>
                             <span className="text-xs text-slate-400 font-mono mt-1 block">ID: field_{field?.id || '---'} | Type: {field?.field_type || '---'}</span>
                          </div>
                       </div>

                       {field?.conditions && field?.conditions?.length > 0 && (
                          <div className="mb-4 bg-indigo-50/50 p-3 rounded-xl border border-indigo-100 text-xs font-medium text-indigo-800/80 space-y-2">
                             <div className="flex items-center gap-1 font-bold text-indigo-600"><Link2 size={12}/> شروط وابستگی:</div>
                             {field?.conditions?.map((cond, cIdx) => (
                                <div key={cond?.id || cIdx} className="flex items-start gap-1">
                                   <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0"></div>
                                   <span>{getConditionText(cond)}</span>
                                </div>
                             ))}
                          </div>
                       )}

                       {field?.choices && field?.choices?.length > 0 && (
                          <div className="space-y-2 mt-4 border-t border-slate-100 pt-4">
                             <div className="text-xs font-bold text-slate-500 mb-2">گزینه‌های قابل انتخاب:</div>
                             {field?.choices?.map((choice, chIdx) => (
                                <div key={choice?.id || chIdx} className="flex justify-between items-center text-sm p-2 bg-slate-50 rounded-lg">
                                   <span className="font-bold text-slate-700 flex items-center gap-2">
                                      <Check size={14} className="text-indigo-400"/> {choice?.title || 'بدون نام'}
                                   </span>
                                   {parseFloat(choice?.numeric_value || 0) > 0 && (
                                      <span className="font-mono text-indigo-600 font-bold bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100 dir-ltr text-xs">
                                         +{formatPrice(choice?.numeric_value)} <span className="text-[9px]">IQD</span>
                                      </span>
                                   )}
                                </div>
                             ))}
                          </div>
                       )}
                    </div>
                 ))}
              </div>
           )}
        </div>

        {/* ROW 3: Formulas & Attachments */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
           
           {/* Formulas */}
           <div dir='ltr' className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 rounded-[2rem]">
              <div className="flex items-center gap-4 mb-6 pb-4 border-b border-slate-100">
                 <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                    <Calculator size={24} />
                 </div>
                 <div>
                    <h3 className="text-xl font-black text-slate-800">فرمول‌های محاسباتی</h3>
                    <p className="text-sm text-slate-500 font-medium mt-1">فرمول‌های تعیین قیمت نهایی</p>
                 </div>
              </div>

              {formulas.length === 0 ? (
                 <div className="text-center py-8 text-slate-400 font-bold text-sm bg-slate-50 rounded-2xl">فرمولی ثبت نشده است.</div>
              ) : (
                 <div className="space-y-4">
                    {formulas.map((f, fIdx) => (
                       <div key={f?.id || fIdx} className="border border-purple-100 bg-purple-50/30 p-5 rounded-2xl">
                          <h4 className="font-black text-purple-800 text-sm mb-3">{f?.title || `فرمول #${f?.id || ''}`}</h4>
                          <div className="space-y-3">
                             {f?.condition_expression && (
                                <div className="bg-white/60 p-3 rounded-xl border border-purple-100/50">
                                   <span className="text-xs font-bold text-purple-600/70 block mb-1">شرط اجرا:</span>
                                   <code className="text-sm font-bold text-purple-800 dir-ltr block text-left">{f?.condition_expression}</code>
                                </div>
                             )}
                             <div className="bg-white p-3 rounded-xl border border-purple-200 shadow-sm">
                                <span className="text-xs font-bold text-emerald-600 block mb-1">فرمول محاسبه:</span>
                                <code className="text-sm font-black text-emerald-700 dir-ltr block text-left">{f?.calculation_expression || '---'}</code>
                             </div>
                          </div>
                       </div>
                    ))}
                 </div>
              )}
           </div>

           {/* Attachments */}
           <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 rounded-[2rem]">
              <div className="flex items-center gap-4 mb-6 pb-4 border-b border-slate-100">
                 <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
                    <Paperclip size={24} />
                 </div>
                 <div>
                    <h3 className="text-xl font-black text-slate-800">فایل‌های پیوست</h3>
                    <p className="text-sm text-slate-500 font-medium mt-1">اسناد، قالب‌ها و ویدیوهای مرتبط</p>
                 </div>
              </div>

              {attachments.length === 0 ? (
                 <div className="text-center py-8 text-slate-400 font-bold text-sm bg-slate-50 rounded-2xl">فایل پیوستی وجود ندارد.</div>
              ) : (
                 <div className="space-y-3">
                    {attachments.map((att, aIdx) => (
                       <a 
                          key={att?.id || aIdx} 
                          href={att?.file || '#'} 
                          target="_blank" 
                          rel="noreferrer"
                          className="flex items-center gap-4 p-4 bg-white border border-slate-100 rounded-2xl hover:border-rose-200 hover:shadow-md transition-all group"
                       >
                          <div className="w-10 h-10 rounded-full bg-slate-50 text-slate-400 flex items-center justify-center group-hover:bg-rose-50 group-hover:text-rose-500 transition-colors">
                             <Download size={18}/>
                          </div>
                          <div className="flex-1 overflow-hidden">
                             <h5 className="font-bold text-slate-700 text-sm truncate dir-ltr text-right">{att?.name || 'فایل ضمیمه'}</h5>
                             <span className="text-xs text-slate-400 font-medium">{att?.created_at ? new Date(att?.created_at).toLocaleDateString('fa-IR') : '---'}</span>
                          </div>
                       </a>
                    ))}
                 </div>
              )}
           </div>

        </div>
      </div>
    </div>
  );
};

export default ProductDetailPage;