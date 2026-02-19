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

// --- UI Components ---
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
        <option value="info">آبی</option>
        <option value="tip">زرد</option>
        <option value="warning">نارنجی</option>
        <option value="danger">قرمز</option>
        <option value="success">سبز</option>
    </select>
);

const ProductStep1Form = ({ initialData, onSave, isSaving, isEditMode }) => {
  
  // --- 1. Master Data ---
  const { data: parentCategories = [] } = useQuery({
    queryKey: ['admin-parent-categories'],
    queryFn: () => adminCategoryService.getRoots(),
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
  const [targetSubCategoryId, setTargetSubCategoryId] = useState(null); // ذخیره ID زیردسته مورد نظر

  // دریافت فرزندان بر اساس پدر انتخاب شده
  const { data: parentDetails, isFetching: isLoadingChildren } = useQuery({
    queryKey: ['admin-category-details', selectedParentId],
    queryFn: () => adminCategoryService.getById(selectedParentId),
    enabled: !!selectedParentId,
  });

  // --- 3. Form Setup ---
  const { register, control, handleSubmit, watch, setValue, getValues, reset, formState: { errors } } = useForm({
    resolver: zodResolver(ProductStep1Schema),
    defaultValues: {
      shell: { has_quantity: true, is_active: true, guide_type: 'info', price: "0", name: "", category_id: "" },
      pricing_config: { base_setup_price: 0, design_service_available: false, design_fee: 0, min_quantity: 1 },
      quantities: [],
      sizes: []
    }
  });

  // --- 4. Initialization Logic ---
  useEffect(() => {
    const isMasterDataReady = standardSizes.length > 0 && systemQuantities.length > 0;

    if (initialData && isEditMode && isMasterDataReady) {
        console.log("🔄 Initializing Data...", initialData);

        // A. نرمال‌سازی Category
        let currentCatId = initialData.shell?.category_info?.id || initialData.shell?.category_id;
        
        if (currentCatId) {
            // ذخیره ID هدف برای استفاده ثانویه (بعد از لود شدن لیست)
            setTargetSubCategoryId(currentCatId);

            // پیدا کردن والد برای پر کردن دراپ‌داون اول
            adminCategoryService.getById(currentCatId).then(catData => {
                if (catData?.parent) {
                    setSelectedParentId(catData.parent);
                } else {
                    setSelectedParentId(currentCatId); 
                }
            }).catch(console.error);
        }

        // B. نرمال‌سازی Quantities
        let normalizedQuantities = [];
        if (Array.isArray(initialData.quantities)) {
            normalizedQuantities = initialData.quantities.map(q => {
                const matchedQty = systemQuantities.find(sq => Number(sq.value) === Number(q.value));
                if (matchedQty) {
                    return {
                        id: matchedQty.id,
                        guide_text: q.guide_text || "",
                        guide_type: q.guide_type || "info"
                    };
                }
                return null;
            }).filter(Boolean);
        }

        // C. نرمال‌سازی Sizes
        let normalizedSizes = [];
        const sizesArray = initialData.sizes?.sizes || (Array.isArray(initialData.sizes) ? initialData.sizes : []);
        
        if (sizesArray.length > 0) {
            normalizedSizes = sizesArray.map(s => {
                const matchedSize = standardSizes.find(ss => 
                    Number(ss.width) === Number(s.width) && 
                    Number(ss.height) === Number(s.height)
                );

                if (matchedSize) {
                    return {
                        id: matchedSize.id,
                        price_impact: Number(s.price || 0),
                        guide_text: s.guide_text || "",
                        guide_type: s.guide_type || "info"
                    };
                }
                return null;
            }).filter(Boolean);
        }

        // D. پر کردن فرم
        reset({
            shell: {
                ...initialData.shell,
                name: initialData.shell.name,
                category_id: currentCatId || "",
                price: String(initialData.shell.price || "0"),
                guide_text: initialData.shell.guide_text || "",
                guide_type: initialData.shell.guide_type || "info"
            },
            pricing_config: {
                ...initialData.pricing_config,
                base_setup_price: Number(initialData.pricing_config.base_setup_price || 0),
                design_fee: Number(initialData.pricing_config.design_fee || 0),
            },
            quantities: normalizedQuantities,
            sizes: normalizedSizes,
        });
    }
  }, [initialData, isEditMode, reset, standardSizes, systemQuantities]);

  // --- 5. Fix: Re-apply SubCategory when List Loads ---
  // این افکت زمانی اجرا می‌شود که لیست فرزندان (parentDetails) از سرور برسد
  useEffect(() => {
      if (parentDetails?.children && targetSubCategoryId) {
          // چک می‌کنیم آیا زیردسته هدف در لیست جدید وجود دارد؟
          const exists = parentDetails.children.find(c => Number(c.id) === Number(targetSubCategoryId));
          if (exists) {
              // اگر بود، دوباره مقدار را در فرم ست می‌کنیم تا نمایش داده شود
              setValue('shell.category_id', targetSubCategoryId);
          }
      }
  }, [parentDetails, targetSubCategoryId, setValue]);


  // Watchers
  const hasQuantity = watch('shell.has_quantity');
  const designAvailable = watch('pricing_config.design_service_available');
  
  const { fields: qtyFields, append: appendQty, remove: removeQty } = useFieldArray({ control, name: "quantities" });
  const { fields: sizeFields, append: appendSize, remove: removeSize } = useFieldArray({ control, name: "sizes" });

  // Handlers
  const handleParentChange = (e) => {
    const val = e.target.value;
    setSelectedParentId(val);
    setValue('shell.category_id', ''); // در تغییر دستی، مقدار قبلی پاک شود
    setTargetSubCategoryId(null); // هدف قبلی را هم پاک می‌کنیم
  };

  const handleAddQuantity = (e) => {
    const qtyId = e.target.value;
    if (!qtyId) return;
    
    const currentQuantities = watch('quantities') || [];
    const exists = currentQuantities.find(q => String(q.id) === String(qtyId));
    
    if (exists) {
        toast.error("این تیراژ قبلاً اضافه شده است");
        return;
    }

    appendQty({ id: Number(qtyId), guide_text: "", guide_type: "info" });
    e.target.value = ""; 
  };

  return (
    <form onSubmit={handleSubmit(onSave)} className="w-full max-w-5xl mx-auto pb-32 space-y-10">
      
      {/* === CARD 1: Basic Info === */}
      <div className="card bg-white shadow-xl shadow-slate-200/40 border border-slate-100 p-8 rounded-[2rem]">
          <SectionTitle icon={Box} title="اطلاعات پایه محصول" desc="مشخصات عمومی و دسته‌بندی" />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="form-control md:col-span-2">
                  <label className="label text-sm font-bold text-slate-700 mb-1">نام محصول <span className="text-error">*</span></label>
                  <input 
                      {...register('shell.name')} 
                      className="input input-lg input-bordered w-full rounded-2xl bg-slate-50 focus:bg-white text-base font-bold text-slate-800" 
                      placeholder="مثال: کارت ویزیت لمینت براق"
                  />
                  <FormError message={errors.shell?.name?.message} />
              </div>

              {/* دسته بندی - مرحله ۱: والد */}
              <div className="form-control">
                  <label className="label text-sm font-bold text-slate-700 mb-1">۱. گروه اصلی</label>
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
                      ۲. زیر دسته (محصول نهایی) <span className="text-error">*</span>
                      {isLoadingChildren && <span className="loading loading-spinner loading-xs mr-2 text-primary"></span>}
                  </label>
                  <select 
                     {...register('shell.category_id')} 
                     className="select select-lg select-bordered w-full rounded-2xl bg-white text-base"
                     disabled={!selectedParentId}
                  >
                      <option value="">
                          {selectedParentId ? '-- انتخاب کنید --' : 'ابتدا گروه را انتخاب کنید'}
                      </option>
                      {parentDetails?.children?.map(child => (
                          <option key={child.id} value={child.id}>{child.name}</option>
                      ))}
                      {parentDetails && !parentDetails.children?.length && (
                          <option value={parentDetails.id}>{parentDetails.name} (بدون زیرمجموعه)</option>
                      )}
                  </select>
                  <FormError message={errors.shell?.category_id?.message} />
              </div>

              {/* توضیحات */}
              <div className="form-control md:col-span-2">
                  <label className="label text-sm font-bold text-slate-700 mb-1">توضیحات</label>
                  <textarea 
                      {...register('shell.description')}
                      className="textarea textarea-bordered h-24 rounded-2xl bg-slate-50 text-base"
                  ></textarea>
              </div>

              <div className="form-control md:col-span-2 bg-slate-50 p-4 rounded-2xl flex flex-col md:flex-row gap-4 items-end">
                   <div className="w-full">
                        <label className="label text-xs font-bold text-slate-500 mb-1">متن راهنما (مثل: زمان تحویل)</label>
                        <div className="flex gap-2">
                            <input {...register('shell.guide_text')} className="input input-bordered w-full bg-white"/>
                            <GuideTypeSelector register={register} name="shell.guide_type" />
                        </div>
                   </div>
                   <div className="form-control min-w-[150px]">
                       <label className="cursor-pointer label justify-start gap-3">
                           <input type="checkbox" {...register('shell.is_active')} className="toggle toggle-success" />
                           <span className="label-text font-bold text-slate-700">محصول فعال</span>
                       </label>
                   </div>
              </div>
          </div>
      </div>

      {/* === CARD 2: Pricing Strategy === */}
      <div className="card bg-white shadow-xl shadow-slate-200/40 border border-slate-100 p-8 rounded-[2rem]">
          <SectionTitle icon={Calculator} title="استراتژی قیمت‌گذاری" desc="نحوه محاسبه قیمت برای مشتری" />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
               <div 
                  onClick={() => setValue('shell.has_quantity', true)}
                  className={clsx(
                      "cursor-pointer rounded-3xl p-6 border-2 transition-all flex items-center gap-4",
                      hasQuantity ? "border-blue-500 bg-blue-50" : "border-slate-100 bg-white"
                  )}
               >
                   <div className={clsx("p-3 rounded-xl", hasQuantity ? "bg-blue-500 text-white" : "bg-slate-100 text-slate-400")}>
                       <Printer size={28} />
                   </div>
                   <div>
                       <h4 className={clsx("font-bold text-lg", hasQuantity ? "text-blue-700" : "text-slate-600")}>تیراژی (پکی)</h4>
                       <p className="text-xs text-slate-500 mt-1">مثل کارت ویزیت (۱۰۰۰تایی، ۲۰۰۰تایی)</p>
                   </div>
               </div>

               <div 
                  onClick={() => setValue('shell.has_quantity', false)}
                  className={clsx(
                      "cursor-pointer rounded-3xl p-6 border-2 transition-all flex items-center gap-4",
                      !hasQuantity ? "border-emerald-500 bg-emerald-50" : "border-slate-100 bg-white"
                  )}
               >
                   <div className={clsx("p-3 rounded-xl", !hasQuantity ? "bg-emerald-500 text-white" : "bg-slate-100 text-slate-400")}>
                       <MousePointerClick size={28} />
                   </div>
                   <div>
                       <h4 className={clsx("font-bold text-lg", !hasQuantity ? "text-emerald-700" : "text-slate-600")}>تعدادی / متری</h4>
                       <p className="text-xs text-slate-500 mt-1">مثل بنر یا ریسو (تعداد دلخواه مشتری)</p>
                   </div>
               </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-slate-50/50 p-6 rounded-3xl border border-slate-100">
              <div className="form-control">
                  <label className="label text-sm font-bold text-slate-700">قیمت پایه (تومان)</label>
                  <div className="relative">
                      <input 
                          {...register('shell.price')}
                          className="input input-lg input-bordered w-full pl-10 font-mono text-xl font-bold text-emerald-600 dir-ltr bg-white"
                          placeholder="0"
                      />
                      <DollarSign className="absolute left-3 top-4 text-emerald-500" size={20}/>
                  </div>
                  <FormError message={errors.shell?.price?.message} />
              </div>

              {/* <div className="form-control">
                  <label className="label text-sm font-bold text-slate-700">هزینه ثابت (Setup)</label>
                  <input 
                      type="number" {...register('pricing_config.base_setup_price')}
                      className="input input-lg input-bordered w-full font-mono dir-ltr bg-white"
                  />
              </div> */}

              {!hasQuantity && (
                  <div className="form-control">
                      <label className="label text-sm font-bold text-slate-700">محدوده تعداد سفارش</label>
                      <div className="flex gap-2">
                          <input type="number" {...register('pricing_config.min_quantity')} className="input input-lg input-bordered w-full bg-white text-center" placeholder="Min"/>
                          <input type="number" {...register('pricing_config.max_quantity')} className="input input-lg input-bordered w-full bg-white text-center" placeholder="Max"/>
                      </div>
                  </div>
              )}
          </div>

          <div className="mt-6 pt-6 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4">
               <div className="flex items-center gap-3">
                   <div className="p-2 bg-purple-50 text-purple-600 rounded-lg"><Palette size={20}/></div>
                   <h5 className="font-bold text-slate-800 text-sm">امکان سفارش طراحی آنلاین دارد؟</h5>
               </div>
               <div className="flex items-center gap-4">
                   <input type="checkbox" {...register('pricing_config.design_service_available')} className="toggle toggle-primary" />
                   {designAvailable && (
                       <input type="number" {...register('pricing_config.design_fee')} className="input input-bordered input-sm w-36" placeholder="هزینه طراحی"/>
                   )}
               </div>
          </div>
      </div>

      {/* === CARD 3: Sizes & Quantities === */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          
          {/* Sizes */}
          <div className="card bg-white shadow-xl p-8 rounded-[2rem] border border-slate-100">
              <div className="flex justify-between items-center mb-6">
                  <SectionTitle icon={Ruler} title="سایزهای محصول" />
                  <button type="button" onClick={() => appendSize({ id: "", price_impact: 0 })} className="btn btn-primary btn-sm btn-outline">
                     <Plus size={16}/> افزودن
                  </button>
              </div>
              <div className="space-y-4">
                  {sizeFields.map((field, index) => (
                      <div key={field.id} className="p-4 bg-slate-50 rounded-2xl flex flex-col gap-3 relative group hover:bg-slate-100 transition-colors">
                          <button onClick={() => removeSize(index)} className="btn btn-xs btn-circle btn-error absolute -top-2 -left-2 opacity-0 group-hover:opacity-100 transition-opacity"><Trash2 size={12}/></button>
                          
                          <div className="flex gap-3">
                              <select {...register(`sizes.${index}.id`)} className="select select-bordered w-full bg-white font-bold text-sm">
                                  <option value="">انتخاب سایز...</option>
                                  {standardSizes.map(s => <option key={s.id} value={s.id}>{s.name} ({s.width}×{s.height})</option>)}
                              </select>
                              <input type="number" {...register(`sizes.${index}.price_impact`)} className="input input-bordered w-1/3 font-mono text-emerald-600 bg-white text-sm" placeholder="+ قیمت" />
                          </div>
                          
                          <div className="flex gap-2">
                              <input {...register(`sizes.${index}.guide_text`)} className="input input-xs input-bordered w-full bg-white" placeholder="راهنما"/>
                              <GuideTypeSelector register={register} name={`sizes.${index}.guide_type`} />
                          </div>
                      </div>
                  ))}
                  {sizeFields.length === 0 && <div className="text-center text-xs text-slate-400 py-4">سایزی تعریف نشده است</div>}
              </div>
          </div>

          {/* Quantities */}
          {hasQuantity && (
              <div className="card bg-white shadow-xl p-8 rounded-[2rem] border border-slate-100">
                  <div className="flex justify-between items-center mb-6">
                      <SectionTitle icon={Hash} title="تیراژهای مجاز" />
                      <div className="w-40">
                           <select 
                                className="select select-bordered select-sm w-full font-bold" 
                                onChange={handleAddQuantity}
                           >
                               <option value="">+ افزودن...</option>
                               {systemQuantities.map((q) => (
                                   <option key={q.id} value={q.id}>{Number(q.value).toLocaleString()} عدد</option>
                               ))}
                           </select>
                      </div>
                  </div>

                  <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                      {qtyFields.map((field, index) => {
                         const rowId = watch(`quantities.${index}.id`);
                         const foundQty = systemQuantities.find(q => String(q.id) === String(rowId));
                         const displayValue = foundQty ? Number(foundQty.value).toLocaleString() : '---';
                         
                         return (
                              <div key={field.id} className="p-4 bg-white border border-slate-200 rounded-2xl shadow-sm relative group">
                                  <button onClick={() => removeQty(index)} className="btn btn-xs btn-circle btn-ghost text-error absolute top-2 left-2 opacity-0 group-hover:opacity-100"><Trash2 size={14}/></button>
                                  
                                  <div className="flex justify-between items-center mb-2">
                                      <span className="font-black text-lg text-slate-800">{displayValue} <span className="text-xs text-slate-400">عدد</span></span>
                                  </div>
                                  <div className="flex gap-2">
                                      <input {...register(`quantities.${index}.guide_text`)} className="input input-xs input-bordered w-full bg-slate-50" placeholder="برچسب"/>
                                      <GuideTypeSelector register={register} name={`quantities.${index}.guide_type`} />
                                  </div>
                              </div>
                         );
                      })}
                      {qtyFields.length === 0 && <div className="text-center text-xs text-slate-400 py-4">لیست تیراژ خالی است</div>}
                  </div>
              </div>
          )}
      </div>

      <div className="sticky bottom-4 z-50 flex justify-end">
         <button type="submit" disabled={isSaving} className="btn btn-primary h-14 px-10 rounded-full shadow-2xl shadow-primary/30 text-lg font-bold hover:scale-105 active:scale-95 transition-all">
            {isSaving ? <span className="loading loading-spinner"></span> : <Save size={22}/>}
            {isEditMode ? 'ذخیره تغییرات' : 'ثبت و مرحله بعد'}
         </button>
      </div>
    </form>
  );
};

export default ProductStep1Form;