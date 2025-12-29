import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ArrowRight, Edit, Trash2, Box, Layers, Ruler, 
  DollarSign, CheckCircle2, XCircle, Info, Image as ImageIcon,
  Settings, FileText, List, Type, CheckSquare, Calendar, MonitorPlay
} from 'lucide-react';
import { adminProductService } from '../../services/adminProductService';
import { adminCategoryService } from '../../services/adminCategoryService';
import clsx from 'clsx';

// تابع کمکی برای فرمت قیمت
const formatPrice = (price) => {
  if (!price) return '0';
  const num = parseFloat(price);
  return new Intl.NumberFormat('fa-IQ').format(num);
};

const ProductDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // 1. دریافت اطلاعات کامل محصول
  const { data: product, isLoading, isError } = useQuery({
    queryKey: ['admin-product', id],
    queryFn: () => adminProductService.getById(id),
    retry: 1
  });

  // 2. دریافت لیست دسته‌ها برای پیدا کردن نام دسته
  const { data: categories } = useQuery({
    queryKey: ['admin-categories'],
    queryFn: adminCategoryService.getAll,
    enabled: !!product?.shell?.category_info, // اگر آی‌دی دسته در شل بود (در مثال شما category_info استرینگ بود، اگر آی‌دی عددی دارید اینجا استفاده کنید)
  });

  if (isLoading) return (
    <div className="h-[70vh] flex flex-col items-center justify-center gap-4">
       <span className="loading loading-spinner loading-lg text-primary"></span>
       <p className="text-slate-400 font-medium animate-pulse">در حال دریافت جزئیات محصول...</p>
    </div>
  );

  if (isError || !product) return (
    <div className="h-[50vh] flex flex-col items-center justify-center text-slate-400 gap-4">
        <Box size={48} strokeWidth={1.5} />
        <p>محصول مورد نظر یافت نشد یا مشکلی در ارتباط وجود دارد.</p>
        <button onClick={() => navigate(-1)} className="btn btn-outline btn-sm">بازگشت</button>
    </div>
  );

  // Destructuring Data for cleaner access
  const { shell, pricing_config, quantities, sizes, images, options } = product;

  // هندل کردن safe data (چون در مثال شما برخی فیلدها string بودند ولی احتمالاً آرایه هستند)
  // اگر بکند استرینگ برمی‌گرداند باید JSON.parse شود، اما من اینجا فرض را بر آرایه بودن می‌گذارم.
  const safeQuantities = Array.isArray(quantities) ? quantities : []; 
  const safeSizes = Array.isArray(sizes) ? sizes : [];
  
  return (
    <div className=" max-w-[1600px] mx-auto space-y-6 pb-32 animate-fade-in-up">
      
      {/* --- HEADER --- */}
      <div className="flex flex-col md:flex-row justify-between items-start gap-4 border-b border-base-200 pb-6 bg-white/50 backdrop-blur-sm sticky top-0 z-10 p-4 rounded-b-2xl -mx-4 -mt-4 shadow-sm">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/admin/products')} className="btn btn-circle btn-ghost btn-sm text-slate-500 hover:bg-slate-100">
             <ArrowRight size={22}/>
          </button>
          
          <div className="flex gap-4 items-center">
              {/* Product Thumbnail */}
              <div className="avatar">
                  <div className="w-16 h-16 rounded-xl ring-1 ring-slate-200 shadow-sm bg-white p-1">
                      {images && images.length > 0 ? (
                          <img src={images[0].image} alt={shell.name} className="object-cover rounded-lg"/>
                      ) : (
                          <div className="w-full h-full flex items-center justify-center text-slate-300 bg-slate-50 rounded-lg">
                             <Box size={24}/>
                          </div>
                      )}
                  </div>
              </div>
              
              <div>
                  <h1 className="text-2xl font-black text-slate-800 flex items-center gap-2">
                    {shell.name}
                    {shell.is_active ? (
                        <div className="badge badge-success badge-sm gap-1 text-white text-xs">فعال</div>
                    ) : (
                        <div className="badge badge-error badge-sm gap-1 text-white text-xs">غیرفعال</div>
                    )}
                  </h1>
                  <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-500 font-mono">
                      <span className="bg-slate-100 px-2 py-0.5 rounded text-slate-600 font-bold tracking-wider">
                         {shell.code || 'NO-CODE'}
                      </span>
                      <span className="flex items-center gap-1 dir-ltr opacity-70">
                         /{shell.slug}
                      </span>
                  </div>
              </div>
          </div>
        </div>

        <div className="flex gap-2">
           <Link to={`/admin/products/edit/${id}`} className="btn btn-primary btn-sm px-4 shadow-lg shadow-primary/20 gap-2 rounded-lg font-bold">
              <Edit size={16}/> ویرایش
           </Link>
           <button className="btn btn-error btn-outline btn-sm btn-square rounded-lg" title="حذف محصول">
              <Trash2 size={16}/>
           </button>
        </div>
      </div>

      {/* --- MAIN GRID LAYOUT --- */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
          
          {/* === LEFT COLUMN (DETAILS) === */}
          <div className="xl:col-span-8 space-y-6">
              
              {/* 1. Basic Information & Config */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  
                  {/* Info Card */}
                  <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                      <h3 className="font-bold text-slate-800 text-sm mb-4 flex items-center gap-2">
                         <Info size={18} className="text-primary"/> توضیحات و مشخصات
                      </h3>
                      <p className="text-sm text-slate-600 leading-7 text-justify bg-slate-50 p-4 rounded-xl border border-slate-100 min-h-[120px]">
                          {shell.description || 'توضیحاتی ثبت نشده است.'}
                      </p>
<div className="mt-4 flex flex-wrap gap-2">
   {shell.category_info && (
       <span className="badge badge-ghost gap-1 pl-3 py-3">
          <Layers size={14}/> 
          {/* ✅ اصلاح شده: بررسی می‌کنیم اگر آبجکت بود، فقط نام را نشان بده */}
          {typeof shell.category_info === 'object' 
              ? shell.category_info.name 
              : shell.category_info}
       </span>
   )}
   
   <span className="badge badge-ghost gap-1 pl-3 py-3">
      <Calendar size={14}/> {new Date(shell.created_at).toLocaleDateString('fa-IR')}
   </span>
</div>
                  </div>

                  {/* Pricing Config Card */}
                  <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm relative overflow-hidden">
                      <div className="absolute -right-6 -top-6 w-24 h-24 bg-emerald-50 rounded-full blur-xl"></div>
                      <h3 className="font-bold text-slate-800 text-sm mb-4 flex items-center gap-2 relative z-10">
                         <DollarSign size={18} className="text-emerald-600"/> قوانین قیمت‌گذاری
                      </h3>
                      
                      <div className="space-y-3 relative z-10">
                          <ConfigItem 
                             label="قیمت پایه محصول" 
                             value={`${formatPrice(shell.price)} IQD`} 
                             isPrice 
                          />
                          <ConfigItem 
                             label="هزینه ثابت (Setup Price)" 
                             value={`${formatPrice(pricing_config.base_setup_price)} IQD`} 
                             isPrice 
                          />
                          <ConfigItem 
                             label="هزینه طراحی" 
                             value={pricing_config.design_service_available ? `${formatPrice(pricing_config.design_fee)} IQD` : 'ندارد'} 
                          />
                          <div className="divider my-1"></div>
                          <div className="grid grid-cols-2 gap-2 text-xs">
                             <BooleanTag label="ابعاد دلخواه" value={pricing_config.accepts_custom_dimensions} />
                             <BooleanTag label="تعداد دلخواه" value={pricing_config.allow_custom_quantity} />
                             <BooleanTag label="خدمات طراحی" value={pricing_config.design_service_available} />
                          </div>
                      </div>
                  </div>
              </div>

              {/* 2. OPTIONS (Form Builder Visualization) - CRITICAL PART */}
              <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                  <div className="p-5 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
                     <div>
                        <h3 className="font-bold text-slate-800 flex items-center gap-2">
                            <List size={20} className="text-purple-600"/> 
                            ویژگی‌های محصول (فرم سفارش)
                        </h3>
                        <p className="text-xs text-slate-500 mt-1">آپشن‌هایی که مشتری هنگام خرید باید انتخاب کند</p>
                     </div>
                     <span className="badge badge-neutral text-xs">{options?.length || 0} فیلد</span>
                  </div>

                  <div className="p-5 grid grid-cols-1 gap-4">
                      {options && options.length > 0 ? (
                          options.map((opt) => (
                              <div key={opt.id} className="border border-slate-200 rounded-xl p-4 hover:border-purple-200 hover:shadow-md transition-all group bg-white">
                                  {/* Option Header */}
                                  <div className="flex justify-between items-start mb-3">
                                      <div className="flex items-center gap-3">
                                          <div className="p-2 bg-purple-50 text-purple-600 rounded-lg">
                                              {getIconForInputType(opt.input_type)}
                                          </div>
                                          <div>
                                              <h4 className="font-bold text-slate-700 text-sm">{opt.label}</h4>
                                              <span className="text-[10px] text-slate-400 font-mono bg-slate-100 px-1.5 rounded ml-2">{opt.name}</span>
                                          </div>
                                      </div>
                                      <div className="flex gap-2">
                                          {opt.is_required && <span className="badge badge-error badge-xs badge-outline font-bold">اجباری</span>}
                                          <span className="badge badge-ghost badge-xs">{translateInputType(opt.input_type)}</span>
                                      </div>
                                  </div>

                                  {/* Choices / Values */}
                                  {opt.choices && opt.choices.length > 0 ? (
                                      <div className="mt-3 flex flex-wrap gap-2">
                                          {opt.choices.map((choice) => (
                                              <div key={choice.id} className="flex items-center gap-2 bg-slate-50 border border-slate-100 rounded-lg px-3 py-1.5 text-xs">
                                                  <span className="font-medium text-slate-700">{choice.label}</span>
                                                  {parseFloat(choice.price_impact) !== 0 && (
                                                      <span className={clsx(
                                                          "font-mono dir-ltr font-bold",
                                                          parseFloat(choice.price_impact) > 0 ? "text-emerald-600" : "text-red-500"
                                                      )}>
                                                          {parseFloat(choice.price_impact) > 0 ? '+' : ''}
                                                          {formatPrice(choice.price_impact)}
                                                      </span>
                                                  )}
                                                  {choice.is_default && <CheckCircle2 size={12} className="text-primary ml-1" title="پیش‌فرض"/>}
                                              </div>
                                          ))}
                                      </div>
                                  ) : (
                                    <div className="text-xs text-slate-400 italic bg-slate-50 p-2 rounded">
                                        بدون گزینه از پیش تعریف شده (ورودی کاربر)
                                    </div>
                                  )}
                                  
                                  {opt.guide_text && (
                                      <div className="mt-3 text-[11px] text-slate-400 flex items-start gap-1">
                                          <Info size={12} className="mt-0.5 shrink-0"/> {opt.guide_text}
                                      </div>
                                  )}
                              </div>
                          ))
                      ) : (
                          <div className="text-center py-10 text-slate-400 border-2 border-dashed border-slate-100 rounded-xl">
                              هیچ ویژگی (Option) برای این محصول تعریف نشده است.
                          </div>
                      )}
                  </div>
              </div>

          </div>

          {/* === RIGHT COLUMN (SIDEBAR) === */}
          <div className="xl:col-span-4 space-y-6">
              
              {/* Gallery */}
              <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
                  <h3 className="font-bold text-slate-800 text-sm mb-4 flex items-center gap-2">
                      <ImageIcon size={18} className="text-blue-500"/> گالری تصاویر
                  </h3>
                  <div className="grid grid-cols-3 gap-2">
                      {images?.map((img) => (
                          <div key={img.id} className="relative aspect-square group cursor-pointer overflow-hidden rounded-lg border border-slate-100">
                              <img src={img.image} alt="Product" className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"/>
                              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors"></div>
                              <span className="absolute bottom-1 right-1 bg-black/50 text-white text-[8px] px-1.5 rounded backdrop-blur-sm">
                                  Order: {img.order}
                              </span>
                          </div>
                      ))}
                      {(!images || images.length === 0) && (
                          <div className="col-span-3 py-8 text-center bg-slate-50 rounded-lg text-xs text-slate-400">
                              تصویری موجود نیست
                          </div>
                      )}
                  </div>
              </div>

              {/* Quantities Table (Tiered Pricing) */}
              {shell.has_quantity && (
                  <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                      <div className="p-4 bg-slate-50/50 border-b border-slate-100">
                          <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                              <Layers size={18} className="text-orange-500"/> لیست قیمت تیراژ
                          </h3>
                      </div>
                      <div className="max-h-64 overflow-y-auto custom-scrollbar">
                         {safeQuantities.length > 0 ? (
                             <table className="table table-xs w-full">
                                 <thead>
                                    <tr>
                                        <th>تعداد</th>
                                        <th className="text-left">قیمت (IQD)</th>
                                    </tr>
                                 </thead>
                                 <tbody>
                                     {safeQuantities.map((q, idx) => (
                                         <tr key={idx} className="hover:bg-slate-50">
                                             <td className="font-bold">{q.value || q}</td>
                                             <td className="font-mono dir-ltr text-right text-emerald-600">
                                                {/* هندل کردن حالتی که دیتا ناقص باشد */}
                                                {q.price ? formatPrice(q.price) : '---'}
                                             </td>
                                         </tr>
                                     ))}
                                 </tbody>
                             </table>
                         ) : (
                             <div className="p-6 text-center text-xs text-slate-400">لیست تیراژ خالی است</div>
                         )}
                      </div>
                  </div>
              )}

              {/* Standard Sizes */}
              <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
                  <h3 className="font-bold text-slate-800 text-sm mb-4 flex items-center gap-2">
                      <Ruler size={18} className="text-slate-500"/> سایزهای استاندارد
                  </h3>
                  <div className="flex flex-wrap gap-2">
                      {safeSizes.length > 0 ? safeSizes.map((s, idx) => (
                          <span key={idx} className="badge badge-ghost border border-slate-200 bg-white py-3 text-xs">
                             {/* فرض بر اینکه سایز آبجکت است، اگر استرینگ بود هندل شود */}
                             {typeof s === 'string' ? s : `${s.width || '?'}x${s.height || '?'} cm`}
                          </span>
                      )) : (
                          <span className="text-xs text-slate-400">سایز محدود تعریف نشده است.</span>
                      )}
                  </div>
              </div>

          </div>
      </div>
    </div>
  );
};

// --- Sub-Components (برای تمیزی کد) ---

const ConfigItem = ({ label, value, isPrice }) => (
    <div className="flex justify-between items-center text-sm py-1 border-b border-slate-50 last:border-0">
        <span className="text-slate-500">{label}</span>
        <span className={clsx("font-medium", isPrice ? "text-emerald-600 dir-ltr font-mono" : "text-slate-800")}>
            {value}
        </span>
    </div>
);

const BooleanTag = ({ label, value }) => (
    <div className={clsx(
        "flex items-center gap-1.5 px-3 py-2 rounded-lg border transition-colors",
        value ? "bg-emerald-50 border-emerald-100 text-emerald-700" : "bg-slate-50 border-slate-100 text-slate-400"
    )}>
        {value ? <CheckCircle2 size={14}/> : <XCircle size={14}/>}
        <span>{label}</span>
    </div>
);

// تشخیص آیکون برای نوع اینپوت
const getIconForInputType = (type) => {
    switch (type) {
        case 'text': return <Type size={18}/>;
        case 'textarea': return <FileText size={18}/>;
        case 'select': case 'radio': return <List size={18}/>;
        case 'checkbox': return <CheckSquare size={18}/>;
        case 'file': return <ImageIcon size={18}/>; // یا Upload
        default: return <Settings size={18}/>;
    }
};

// ترجمه نوع اینپوت
const translateInputType = (type) => {
    const map = {
        'text': 'متنی کوتاه',
        'textarea': 'متنی بلند',
        'number': 'عددی',
        'select': 'لیست کشویی',
        'radio': 'تک انتخابی',
        'checkbox': 'چند انتخابی',
        'file': 'آپلود فایل',
    };
    return map[type] || type;
};

export default ProductDetailPage;