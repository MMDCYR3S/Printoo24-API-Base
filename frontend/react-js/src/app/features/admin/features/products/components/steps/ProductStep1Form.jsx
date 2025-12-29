// src/app/features/admin/products/components/steps/ProductStep1Form.jsx
import React, { useState, useEffect } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { 
  Box, Calculator, Ruler, Hash, AlertTriangle, 
  Save, Printer, MousePointerClick, Trash2, 
  Plus, DollarSign, Palette
} from 'lucide-react';
import clsx from 'clsx';
import { useQuery } from '@tanstack/react-query';
import { ProductStep1Schema } from '../../schemas/productSchemas';
import { adminCategoryService } from '../../../../services/adminCategoryService';
import { adminProductService } from '../../../../services/adminProductService';
import toast from 'react-hot-toast';

// --- Components ---
const SectionTitle = ({ icon: Icon, title, desc }) => (
  <div className="flex items-start gap-4 mb-8 border-b border-slate-100 pb-5">
    <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl shadow-sm">
       <Icon size={28} strokeWidth={1.5} />
    </div>
    <div>
      <h3 className="font-extrabold text-slate-800 text-xl tracking-tight">{title}</h3>
      {desc && <p className="text-sm text-slate-500 mt-1 font-medium">{desc}</p>}
    </div>
  </div>
);

const FormError = ({ message }) => (
  message ? (
    <div className="text-error text-[11px] mt-2 flex items-center gap-1.5 font-bold bg-red-50 p-2 rounded-lg animate-pulse">
        <AlertTriangle size={14}/> {message}
    </div>
  ) : null
);

const GuideTypeSelector = ({ register, name }) => (
    <select {...register(name)} className="select select-bordered select-sm w-24 bg-white text-xs h-10">
        <option value="info">آبی (Info)</option>
        <option value="tip">زرد (Tip)</option>
        <option value="warning">نارنجی (Warn)</option>
        <option value="danger">قرمز (Danger)</option>
        <option value="success">سبز (Success)</option>
    </select>
);

const ProductStep1Form = ({ initialData, onSave, isSaving, isEditMode }) => {
  
  // --- 1. Master Data Queries ---
  const { data: parentCategories = [] } = useQuery({
    queryKey: ['admin-parent-categories'],
    queryFn: adminCategoryService.getAll,
  });

  const { data: standardSizes = [] } = useQuery({
    queryKey: ['admin-standard-sizes'],
    queryFn: adminProductService.getStandardSizes,
  });

  const { data: systemQuantities = [] } = useQuery({
    queryKey: ['admin-quantities-list'],
    queryFn: adminProductService.getQuantitiesList, 
  });

  // --- 2. Local State ---
  const [selectedParentId, setSelectedParentId] = useState(null);
  const [isDataReady, setIsDataReady] = useState(!isEditMode); // در حالت جدید دیتا آماده است، در ادیت باید صبر کنیم

  // دریافت فرزندان بر اساس پدر انتخاب شده
  const { data: parentDetails, isFetching: isLoadingChildren } = useQuery({
    queryKey: ['admin-category-details', selectedParentId],
    queryFn: () => adminCategoryService.getById(selectedParentId),
    enabled: !!selectedParentId,
  });

  // --- 3. Form Setup ---
  const { register, control, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm({
    resolver: zodResolver(ProductStep1Schema),
    defaultValues: {
      shell: { has_quantity: true, is_active: true, guide_type: 'info', price: "0", name: "", category_id: "" },
      pricing_config: { base_setup_price: 0, design_service_available: false, design_fee: 0, min_quantity: 1 },
      quantities: [],
      sizes: []
    }
  });

  // --- 4. DATA SYNC & INITIALIZATION (Critical Fix) ---
  useEffect(() => {
    const initializeForm = async () => {
      if (initialData && isEditMode) {
        try {
          console.log("🔄 Initializing form with data:", initialData);

          // A. استخراج ID دسته‌بندی فرزند
          let childId = initialData.shell?.category_id;
          
          // هندل کردن حالتی که category_info آبجکت یا رشته است
          if (!childId && initialData.shell?.category_info) {
             if (typeof initialData.shell.category_info === 'object') {
                childId = initialData.shell.category_info.id;
             } else if (typeof initialData.shell.category_info === 'number') {
                childId = initialData.shell.category_info;
             }
          }

          // B. پیدا کردن پدرِ این دسته‌بندی (Server Lookup)
          if (childId) {
            try {
              // گرفتن اطلاعات کامل دسته فرزند برای فهمیدن والدش
              const catDetail = await adminCategoryService.getById(childId);
              if (catDetail && catDetail.parent) {
                setSelectedParentId(catDetail.parent); // ست کردن والد
              } else {
                // شاید خودش والد باشد یا دیتای والد ندارد
                setSelectedParentId(childId); 
              }
            } catch (err) {
              console.error("❌ Error finding parent category:", err);
            }
          }

          // C. آماده‌سازی داده‌ها برای فرم
          const formattedData = {
            shell: {
              ...initialData.shell,
              category_id: childId || "", // مطمئن می‌شویم ID عددی می‌نشیند
              price: String(initialData.shell.price || "0"), // تبدیل به رشته برای اینپوت
            },
            pricing_config: initialData.pricing_config || {
                base_setup_price: 0, design_service_available: false, design_fee: 0
            },
            // اطمینان از اینکه آرایه است
            quantities: Array.isArray(initialData.quantities) ? initialData.quantities : [],
            sizes: Array.isArray(initialData.sizes) ? initialData.sizes : [],
          };

          reset(formattedData);
          setIsDataReady(true);

        } catch (error) {
          console.error("Form Init Error:", error);
          toast.error("خطا در بارگذاری اطلاعات محصول");
        }
      }
    };

    initializeForm();
    // فقط یکبار اجرا شود (وقتی initialData تغییر کرد)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialData]); 

  // Watchers
  const hasQuantity = watch('shell.has_quantity');
  const designAvailable = watch('pricing_config.design_service_available');
  
  const { fields: qtyFields, append: appendQty, remove: removeQty } = useFieldArray({ control, name: "quantities" });
  const { fields: sizeFields, append: appendSize, remove: removeSize } = useFieldArray({ control, name: "sizes" });

  // Handlers
  const handleParentChange = (e) => {
    const val = e.target.value;
    setSelectedParentId(val);
    setValue('shell.category_id', ''); // وقتی والد عوض شد، فرزند باید خالی شود تا کاربر انتخاب کند
  };

  const handleAddQuantity = (e) => {
    const qtyId = e.target.value;
    if (!qtyId) return;
    
    // جلوگیری از تکراری بر اساس ID (نه value)
    // استفاده از form values به جای fields برای مقایسه دقیق
    const currentQuantities = watch('quantities') || [];
    const exists = currentQuantities.find(q => String(q.id) === String(qtyId));
    
    if (exists) {
        toast.error("این تیراژ قبلاً اضافه شده است");
        return;
    }

    appendQty({ id: Number(qtyId), guide_text: "", guide_type: "info" });
    e.target.value = ""; 
  };

  // اگر در حال لود دیتا برای ادیت هستیم، لودینگ نشان بده
  if (!isDataReady && isEditMode) {
      return <div className="p-20 text-center text-slate-400">در حال آماده‌سازی فرم ویرایش...</div>;
  }

  return (
    <form onSubmit={handleSubmit(onSave)} className="w-full max-w-5xl mx-auto pb-32 space-y-10">
      
      {/* === CARD 1: Basic Info === */}
      <div className="card bg-white shadow-xl shadow-slate-200/40 border border-slate-100 p-8 rounded-[2rem]">
          <SectionTitle icon={Box} title="اطلاعات پایه محصول" desc="مشخصات عمومی جهت نمایش در فروشگاه" />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="form-control md:col-span-2">
                  <label className="label text-sm font-bold text-slate-700 mb-1">نام کامل محصول</label>
                  <input 
                      {...register('shell.name')} 
                      className="input input-lg input-bordered w-full rounded-2xl bg-slate-50 focus:bg-white focus:border-blue-500 transition-all text-base font-bold text-slate-800" 
                      placeholder="مثال: کارت ویزیت لمینت مات"
                  />
                  <FormError message={errors.shell?.name?.message} />
              </div>

              {/* دسته بندی - مرحله ۱: والد */}
              <div className="form-control">
                  <label className="label text-sm font-bold text-slate-700 mb-1">۱. انتخاب گروه اصلی</label>
                  <select 
                     className="select select-lg select-bordered w-full rounded-2xl bg-white text-base"
                     onChange={handleParentChange}
                     value={selectedParentId || ''}
                  >
                      <option value="">-- انتخاب گروه --</option>
                      {parentCategories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
                  </select>
              </div>

              {/* دسته بندی - مرحله ۲: فرزند */}
              <div className="form-control">
                  <label className="label text-sm font-bold text-slate-700 mb-1">
                      ۲. انتخاب محصول (زیر دسته)
                      {isLoadingChildren && <span className="loading loading-spinner loading-xs mr-2 text-primary"></span>}
                  </label>
                  <select 
                     {...register('shell.category_id')} 
                     className="select select-lg select-bordered w-full rounded-2xl bg-white text-base"
                     disabled={!selectedParentId}
                  >
                      <option value="">
                          {selectedParentId ? '-- انتخاب محصول --' : 'ابتدا گروه را انتخاب کنید...'}
                      </option>
                      {parentDetails?.children?.map(child => <option key={child.id} value={child.id}>{child.name}</option>)}
                  </select>
                  <FormError message={errors.shell?.category_id?.message} />
              </div>

              <div className="form-control md:col-span-2">
                  <label className="label text-sm font-bold text-slate-700 mb-1">توضیحات</label>
                  <textarea 
                      {...register('shell.description')}
                      className="textarea textarea-bordered h-28 rounded-2xl bg-slate-50 text-base p-4"
                  ></textarea>
              </div>

              <div className="form-control md:col-span-2 bg-slate-50 p-6 rounded-2xl flex flex-col md:flex-row gap-6 items-end">
                   <div className="w-full">
                        <label className="label text-xs font-bold text-slate-500 mb-1">متن راهنما (مثل: تحویل فوری)</label>
                        <div className="flex gap-2">
                            <input {...register('shell.guide_text')} className="input input-bordered w-full bg-white"/>
                            <GuideTypeSelector register={register} name="shell.guide_type" />
                        </div>
                   </div>
                   <div className="form-control min-w-[150px]">
                       <label className="cursor-pointer label justify-start gap-3">
                           <input type="checkbox" {...register('shell.is_active')} className="toggle toggle-success" />
                           <span className="label-text font-bold text-slate-700">محصول فعال است</span>
                       </label>
                   </div>
              </div>
          </div>
      </div>

      {/* === CARD 2: Strategy & Pricing === */}
      <div className="card bg-white shadow-xl shadow-slate-200/40 border border-slate-100 p-8 rounded-[2rem]">
          <SectionTitle icon={Calculator} title="استراتژی قیمت‌گذاری" desc="تعیین نحوه فروش (تیراژی یا تعدادی)" />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
               {/* Tiered Option */}
               <div 
                  onClick={() => setValue('shell.has_quantity', true)}
                  className={clsx(
                      "relative cursor-pointer rounded-3xl p-8 border-2 transition-all flex items-center gap-6",
                      hasQuantity ? "border-blue-500 bg-blue-50" : "border-slate-100 bg-white"
                  )}
               >
                   <div className={clsx("p-4 rounded-2xl", hasQuantity ? "bg-blue-500 text-white" : "bg-slate-100 text-slate-400")}>
                       <Printer size={32} />
                   </div>
                   <div>
                       <h4 className={clsx("font-black text-lg", hasQuantity ? "text-blue-700" : "text-slate-600")}>فروش تیراژی (پکی)</h4>
                       <p className="text-xs text-slate-500 mt-2">انتخاب بسته‌های مشخص (مثلاً ۱۰۰۰ تایی)</p>
                   </div>
               </div>

               {/* Custom Qty Option */}
               <div 
                  onClick={() => setValue('shell.has_quantity', false)}
                  className={clsx(
                      "relative cursor-pointer rounded-3xl p-8 border-2 transition-all flex items-center gap-6",
                      !hasQuantity ? "border-emerald-500 bg-emerald-50" : "border-slate-100 bg-white"
                  )}
               >
                   <div className={clsx("p-4 rounded-2xl", !hasQuantity ? "bg-emerald-500 text-white" : "bg-slate-100 text-slate-400")}>
                       <MousePointerClick size={32} />
                   </div>
                   <div>
                       <h4 className={clsx("font-black text-lg", !hasQuantity ? "text-emerald-700" : "text-slate-600")}>فروش تعدادی (آزاد)</h4>
                       <p className="text-xs text-slate-500 mt-2">مشتری تعداد دقیق را وارد می‌کند</p>
                   </div>
               </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-slate-50/50 p-6 rounded-3xl border border-slate-100">
              <div className="form-control">
                  <label className="label text-sm font-bold text-slate-700">قیمت پایه واحد</label>
                  <div className="relative">
                      <input 
                          {...register('shell.price')}
                          className="input input-lg input-bordered w-full pl-12 font-mono text-xl font-bold text-emerald-600 dir-ltr bg-white"
                      />
                      <DollarSign className="absolute left-4 top-4 text-emerald-500" size={20}/>
                  </div>
              </div>

              <div className="form-control">
                  <label className="label text-sm font-bold text-slate-700">هزینه ثابت (Setup)</label>
                  <input 
                      type="number" {...register('pricing_config.base_setup_price')}
                      className="input input-lg input-bordered w-full font-mono dir-ltr bg-white"
                  />
              </div>

              {!hasQuantity && (
                  <div className="form-control">
                      <label className="label text-sm font-bold text-slate-700">محدوده تعداد</label>
                      <div className="flex gap-2">
                          <input type="number" {...register('pricing_config.min_quantity')} className="input input-lg input-bordered w-full bg-white text-center" placeholder="Min"/>
                          <input type="number" {...register('pricing_config.max_quantity')} className="input input-lg input-bordered w-full bg-white text-center" placeholder="Max"/>
                      </div>
                  </div>
              )}
          </div>

          {/* Design Toggle */}
          <div className="mt-6 pt-6 border-t border-slate-100 flex items-center justify-between gap-4">
               <div className="flex items-center gap-4">
                   <div className="p-3 bg-purple-50 text-purple-600 rounded-xl"><Palette size={20}/></div>
                   <h5 className="font-bold text-slate-800">سرویس طراحی آنلاین</h5>
               </div>
               <div className="flex items-center gap-4">
                   <input type="checkbox" {...register('pricing_config.design_service_available')} className="toggle toggle-primary toggle-lg" />
                   {designAvailable && (
                       <input type="number" {...register('pricing_config.design_fee')} className="input input-bordered w-40 text-sm" placeholder="هزینه طراحی"/>
                   )}
               </div>
          </div>
      </div>

      {/* === CARD 3: Data Lists === */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          
          {/* Sizes */}
          <div className="card bg-white shadow-xl p-8 rounded-[2rem] border border-slate-100">
              <div className="flex justify-between items-center mb-6">
                  <SectionTitle icon={Ruler} title="سایزهای مجاز" />
                  <button type="button" onClick={() => appendSize({ id: "", price_impact: 0 })} className="btn btn-primary btn-sm">
                     <Plus size={16}/> افزودن
                  </button>
              </div>
              <div className="space-y-4">
                  {sizeFields.map((field, index) => (
                      <div key={field.id} className="p-4 bg-slate-50 rounded-2xl flex flex-col gap-3">
                          <div className="flex gap-3">
                              <select {...register(`sizes.${index}.id`)} className="select select-bordered w-full bg-white font-bold">
                                  <option value="">انتخاب...</option>
                                  {standardSizes.map(s => <option key={s.id} value={s.id}>{s.name} ({s.width}×{s.height})</option>)}
                              </select>
                              <button onClick={() => removeSize(index)} className="btn btn-square btn-ghost text-error"><Trash2 size={18}/></button>
                          </div>
                          <input type="number" {...register(`sizes.${index}.price_impact`)} className="input input-bordered w-full font-mono text-emerald-600 bg-white" placeholder="افزایش قیمت (+)" />
                      </div>
                  ))}
              </div>
          </div>

          {/* Quantities (Fixed Display Issue) */}
          {hasQuantity && (
              <div className="card bg-white shadow-xl p-8 rounded-[2rem] border border-slate-100">
                  <div className="flex justify-between items-center mb-6">
                      <SectionTitle icon={Hash} title="تیراژهای مجاز" />
                      <div className="w-48">
                           <select className="select select-bordered select-sm w-full font-bold" onChange={handleAddQuantity}>
                               <option value="">+ افزودن...</option>
                               {/* مپ کردن لیست مستر دیتا (Value را نشان میدیم، ID را میفرستیم) */}
                               {systemQuantities.map((q) => (
                                   <option key={q.id} value={q.id}>{Number(q.value).toLocaleString()} عدد</option>
                               ))}
                           </select>
                      </div>
                  </div>

                  <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                      {qtyFields.map((field, index) => {
                         // ✅ FIX: استفاده از watch برای خواندن ID واقعی از فرم (نه field.id که داخلی است)
                         const rowId = watch(`quantities.${index}.id`);
                         
                         // پیدا کردن عدد واقعی از روی ID برای نمایش به کاربر
                         const foundQty = systemQuantities.find(q => String(q.id) === String(rowId));
                         const displayValue = foundQty ? Number(foundQty.value).toLocaleString() : '---';
                         
                         return (
                              <div key={field.id} className="flex flex-col gap-3 p-4 bg-white border border-slate-200 rounded-2xl shadow-sm">
                                  <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                                      <span className="font-black text-xl text-slate-800">{displayValue} <span className="text-xs text-slate-400">عدد</span></span>
                                      <button onClick={() => removeQty(index)} className="btn btn-square btn-sm btn-ghost text-error">
                                          <Trash2 size={16}/>
                                      </button>
                                  </div>
                                  <div className="flex gap-2">
                                      <input {...register(`quantities.${index}.guide_text`)} className="input input-sm input-bordered w-full bg-slate-50" placeholder="برچسب"/>
                                      <GuideTypeSelector register={register} name={`quantities.${index}.guide_type`} />
                                  </div>
                              </div>
                         );
                      })}
                      {qtyFields.length === 0 && <div className="text-center py-10 text-slate-400">لیست خالی است</div>}
                  </div>
              </div>
          )}
      </div>

      <div className="sticky bottom-4 z-50 flex justify-end">
         <button type="submit" disabled={isSaving} className="btn btn-primary h-14 px-10 rounded-full shadow-2xl text-lg font-bold">
            {isSaving ? <span className="loading loading-spinner"></span> : <Save size={22}/>}
            {isEditMode ? 'ذخیره تغییرات' : 'مرحله بعد'}
         </button>
      </div>
    </form>
  );
};

export default ProductStep1Form;