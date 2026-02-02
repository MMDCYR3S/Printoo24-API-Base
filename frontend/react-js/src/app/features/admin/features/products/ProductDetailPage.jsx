// src/app/features/admin/products/ProductDetailPage.jsx
import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ArrowRight, Edit, Trash2, Box, Layers, Ruler, 
  DollarSign, CheckCircle2, XCircle, Info, Image as ImageIcon,
  Settings, FileText, List, Type, CheckSquare, Calendar,
  Download, ExternalLink, Paperclip
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

// تابع کمکی برای لینک فایل
const getFileUrl = (url) => {
    if (!url) return '#';
    if (url.startsWith('http') || url.startsWith('blob:')) return url;
    return `http://localhost:9010${url}`;
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

  // 2. دریافت اطلاعات دسته‌بندی فعلی (برای پیدا کردن والد)
  const categoryId = product?.shell?.category_info?.id;
  const { data: currentCategory } = useQuery({
    queryKey: ['category-details', categoryId],
    queryFn: () => adminCategoryService.getById(categoryId),
    enabled: !!categoryId,
    staleTime: 1000 * 60 * 5 // کش کردن برای جلوگیری از درخواست تکراری
  });

  // 3. دریافت اطلاعات دسته‌بندی والد (اگر وجود داشته باشد)
  const parentId = currentCategory?.parent;
  const { data: parentCategory } = useQuery({
    queryKey: ['category-details', parentId],
    queryFn: () => adminCategoryService.getById(parentId),
    enabled: !!parentId,
    staleTime: 1000 * 60 * 5
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

  const { shell, pricing_config, quantities, sizes, images, options, attachments } = product;

  // --- نرمال‌سازی دیتا ---
  const safeQuantities = Array.isArray(quantities) ? quantities : [];
  
  let safeSizes = [];
  if (Array.isArray(sizes)) {
      safeSizes = sizes;
  } else if (sizes && typeof sizes === 'object' && Array.isArray(sizes.sizes)) {
      safeSizes = sizes.sizes;
  }
  
  const safeAttachments = Array.isArray(attachments) ? attachments : [];
  const basePrice = parseFloat(shell.price || 0);

  return (
    <div className="max-w-[1600px] mx-auto space-y-6 pb-32 animate-fade-in-up">
      
      {/* --- HEADER --- */}
      <div className="flex flex-col md:flex-row justify-between items-start gap-4 border-b border-base-200 pb-6 bg-white/80 backdrop-blur-md sticky top-0 z-50 p-4 rounded-b-2xl -mx-4 -mt-4 shadow-sm transition-all">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/admin/products')} className="btn btn-circle btn-ghost btn-sm text-slate-500 hover:bg-slate-100">
             <ArrowRight size={22}/>
          </button>
          
          <div className="flex gap-4 items-center">
              {/* Thumbnail */}
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

      {/* --- MAIN GRID --- */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
          
          {/* === LEFT COLUMN (DETAILS) === */}
          <div className="xl:col-span-8 space-y-6">
              
              {/* 1. Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  
                  {/* Info Card */}
                  <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                      <h3 className="font-bold text-slate-800 text-sm mb-4 flex items-center gap-2">
                         <Info size={18} className="text-primary"/> توضیحات و مشخصات
                      </h3>
                      <p className="text-sm text-slate-600 leading-7 text-justify bg-slate-50 p-4 rounded-xl border border-slate-100 min-h-[120px]">
                          {shell.description || 'توضیحاتی ثبت نشده است.'}
                      </p>
                      
                      {/* ✅ بخش نمایش دسته‌بندی (اصلاح شده) */}
                      <div className="mt-4 flex flex-wrap gap-2">
                         {shell.category_info && (
                             <div className="badge badge-ghost gap-2 pl-4 pr-3 py-4 h-auto">
                                <Layers size={16} className="text-slate-500"/> 
                                <div className="flex flex-col items-start leading-none gap-1">
                                    {/* نام والد */}
                                    {parentCategory && (
                                        <span className="text-[10px] text-slate-400 font-medium">
                                            {parentCategory.name}
                                        </span>
                                    )}
                                    {/* نام زیردسته */}
                                    <span className="font-bold text-slate-700">
                                        {currentCategory?.name || (typeof shell.category_info === 'object' ? shell.category_info.name : shell.category_info)}
                                    </span>
                                </div>
                             </div>
                         )}
                         
                         <span className="badge badge-ghost gap-1 pl-3 py-4 h-auto">
                            <Calendar size={16} className="text-slate-500"/> 
                            <span className="font-bold text-slate-700 dir-ltr">
                                {new Date(shell.created_at).toLocaleDateString('fa-IR')}
                            </span>
                         </span>
                      </div>
                  </div>

                  {/* Pricing Config */}
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

              {/* 2. OPTIONS */}
              <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                  <div className="p-5 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
                     <div>
                        <h3 className="font-bold text-slate-800 flex items-center gap-2">
                            <List size={20} className="text-purple-600"/> 
                            ویژگی‌های محصول (آپشن‌ها)
                        </h3>
                     </div>
                     <span className="badge badge-neutral text-xs">{options?.length || 0} فیلد</span>
                  </div>

                  <div className="p-5 grid grid-cols-1 gap-4">
                      {options && options.length > 0 ? (
                          options.map((opt) => (
                              <div key={opt.id} className="border border-slate-200 rounded-xl p-4 bg-white">
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
                                    <div className="text-xs text-slate-400 italic bg-slate-50 p-2 rounded">بدون گزینه (ورودی کاربر)</div>
                                  )}
                              </div>
                          ))
                      ) : (
                          <div className="text-center py-10 text-slate-400 border-2 border-dashed border-slate-100 rounded-xl">
                              ویژگی تعریف نشده است.
                          </div>
                      )}
                  </div>
              </div>

          </div>

          {/* === RIGHT COLUMN === */}
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
                              <span className="absolute bottom-1 right-1 bg-black/50 text-white text-[8px] px-1.5 rounded backdrop-blur-sm">
                                  #{img.order}
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

              {/* Quantities */}
              {shell.has_quantity && (
                  <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                      <div className="p-4 bg-slate-50/50 border-b border-slate-100">
                          <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                              <Layers size={18} className="text-orange-500"/> لیست قیمت تیراژ
                          </h3>
                      </div>
                      <div className="max-h-64 overflow-y-auto custom-scrollbar p-0">
                         {safeQuantities.length > 0 ? (
                             <table className="table table-sm w-full">
                                 <thead className="bg-slate-50 text-slate-500 text-xs">
                                    <tr>
                                        <th className="text-right pr-6">تعداد (عدد)</th>
                                        <th className="text-left pl-6">قیمت کل (تخمینی)</th>
                                    </tr>
                                 </thead>
                                 <tbody className="text-sm">
                                     {safeQuantities.map((q, idx) => {
                                         const qtyValue = Number(q.value || q);
                                         const calculatedPrice = q.price ? q.price : (qtyValue * basePrice);
                                         return (
                                             <tr key={idx} className="hover:bg-slate-50 border-b border-slate-50 last:border-0">
                                                 <td className="font-bold text-slate-700 pr-6">
                                                     {qtyValue.toLocaleString()}
                                                 </td>
                                                 <td className="text-left pl-6">
                                                     <div className="font-mono dir-ltr font-bold text-emerald-600">
                                                         {formatPrice(calculatedPrice)}
                                                     </div>
                                                     <div className="text-[10px] text-slate-400 font-mono">IQD</div>
                                                 </td>
                                             </tr>
                                         );
                                     })}
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
                          <div key={idx} className="badge badge-lg h-auto py-2 px-3 bg-slate-50 border border-slate-200 text-slate-700 flex flex-col gap-0.5 items-center">
                             <span className="font-bold text-xs">{s.name || 'سایز'}</span>
                             {(s.width && s.height) && (
                                 <span className="text-[10px] text-slate-400 font-mono dir-ltr">
                                     {s.width} × {s.height} cm
                                 </span>
                             )}
                          </div>
                      )) : (
                          <span className="text-xs text-slate-400 bg-slate-50 p-2 rounded w-full text-center border border-dashed border-slate-200">
                              سایز محدود تعریف نشده است.
                          </span>
                      )}
                  </div>
              </div>

              {/* ✅ فایل‌های پیوست */}
              {safeAttachments.length > 0 && (
                  <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
                      <h3 className="font-bold text-slate-800 text-sm mb-4 flex items-center gap-2">
                          <Paperclip size={18} className="text-indigo-500"/> فایل‌های پیوست
                      </h3>
                      <div className="space-y-2">
                          {safeAttachments.map((att) => (
                              <a
                                  key={att.id}
                                  href={getFileUrl(att.file)}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center justify-between p-3 bg-slate-50 border border-slate-100 rounded-xl hover:bg-slate-100 hover:border-indigo-200 transition-all group"
                              >
                                  <div className="flex items-center gap-3">
                                      <div className="p-2 bg-white rounded-lg text-slate-500 group-hover:text-indigo-500 transition-colors shadow-sm">
                                          {att.type === 'video' ? <Film size={16}/> : <FileText size={16}/>}
                                      </div>
                                      <span className="text-xs font-bold text-slate-700 group-hover:text-indigo-700 transition-colors max-w-[150px] truncate">
                                          {att.name || 'فایل ضمیمه'}
                                      </span>
                                  </div>
                                  <ExternalLink size={14} className="text-slate-400 group-hover:text-indigo-500"/>
                              </a>
                          ))}
                      </div>
                  </div>
              )}

          </div>
      </div>
    </div>
  );
};

// --- Sub-Components ---
const ConfigItem = ({ label, value, isPrice }) => (
    <div className="flex justify-between items-center text-sm py-2 border-b border-slate-50 last:border-0">
        <span className="text-slate-500">{label}</span>
        <span className={clsx("font-bold", isPrice ? "text-emerald-600 dir-ltr font-mono" : "text-slate-800")}>
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

const getIconForInputType = (type) => {
    switch (type) {
        case 'text': return <Type size={18}/>;
        case 'textarea': return <FileText size={18}/>;
        case 'select': case 'radio': return <List size={18}/>;
        case 'checkbox': return <CheckSquare size={18}/>;
        case 'file': return <ImageIcon size={18}/>;
        default: return <Settings size={18}/>;
    }
};

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