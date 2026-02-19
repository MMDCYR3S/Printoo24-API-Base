// src/app/features/admin/products/components/steps/ProductStep1Form.jsx
import React, { useState, useEffect } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { 
  Box, Calculator, Ruler, Hash, AlertTriangle, 
  Save, Printer, MousePointerClick, Trash2, 
  Plus, DollarSign, Palette, CheckCircle2
} from 'lucide-react';
import clsx from 'clsx';
import { useQuery } from '@tanstack/react-query';
import { ProductStep1Schema } from '../../schemas/productSchemas';
import { adminCategoryService } from '../../../../services/adminCategoryService';
import { adminProductService } from '../../../../services/adminProductService';
import toast from 'react-hot-toast';

// --- UI Components (Modernized) ---

// کامپوننت تایتل با پشتیبانی از استپ عددی مدرن
const SectionTitle = ({ step, icon: Icon, title, desc }) => (
  <div className="flex items-start gap-5 mb-10 pb-6 border-b border-slate-200/60">
    <div className="relative flex-shrink-0 mt-1">
      <div className="w-14 h-14 rounded-[1.25rem] bg-gradient-to-br from-primary/10 to-primary/5 flex items-center justify-center text-primary shadow-sm border border-primary/10">
         <Icon size={26} strokeWidth={1.5} />
      </div>
      {step && (
        <div className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-primary text-white text-sm font-black flex items-center justify-center shadow-lg shadow-primary/40 border-2 border-white">
          {step}
        </div>
      )}
    </div>
    <div className="pt-1.5">
      <h3 className="font-extrabold text-slate-800 text-2xl tracking-tight">{title}</h3>
      {desc && <p className="text-sm text-slate-500 mt-2 font-medium">{desc}</p>}
    </div>
  </div>
);

// استایل مدرن ارورها
const FormError = ({ message }) => (
  message ? (
    <div className="text-error text-xs mt-2 flex items-center gap-1.5 font-bold animate-in fade-in slide-in-from-top-1">
        <AlertTriangle size={14} className="text-error"/> {message}
    </div>
  ) : null
);

// سلکتور راهنما با طراحی جدید
const GuideTypeSelector = ({ register, name }) => (
    <select {...register(name)} className="bg-transparent border-b-2 border-slate-200 text-xs font-bold text-slate-600 focus:border-primary focus:outline-none transition-colors px-2 py-2 cursor-pointer hover:border-slate-300">
        <option value="info">آبی (Info)</option>
        <option value="tip">زرد (Tip)</option>
        <option value="warning">نارنجی (Warn)</option>
        <option value="danger">قرمز (Danger)</option>
        <option value="success">سبز (Success)</option>
    </select>
);

// کلاس‌های استایل مشترک برای اینپوت‌های زیرخط‌دار (Underline Inputs)
const underlineInputClass = "w-full bg-transparent border-b-2 border-slate-200 px-1 py-3 text-slate-800 placeholder-slate-300 focus:border-primary focus:outline-none transition-all duration-300 hover:border-slate-300";

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
  const [targetSubCategoryId, setTargetSubCategoryId] = useState(null);

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

  // --- 4. Initialization Logic (بدون تغییر) ---
  useEffect(() => {
    const isMasterDataReady = standardSizes.length > 0 && systemQuantities.length > 0;

    if (initialData && isEditMode && isMasterDataReady) {
        let currentCatId = initialData.shell?.category_info?.id || initialData.shell?.category_id;
        
        if (currentCatId) {
            setTargetSubCategoryId(currentCatId);
            adminCategoryService.getById(currentCatId).then(catData => {
                if (catData?.parent) {
                    setSelectedParentId(catData.parent);
                } else {
                    setSelectedParentId(currentCatId); 
                }
            }).catch(console.error);
        }

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

  useEffect(() => {
      if (parentDetails?.children && targetSubCategoryId) {
          const exists = parentDetails.children.find(c => Number(c.id) === Number(targetSubCategoryId));
          if (exists) {
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
    setValue('shell.category_id', ''); 
    setTargetSubCategoryId(null); 
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
    <form onSubmit={handleSubmit(onSave)} className="w-full max-w-5xl mx-auto pb-32 space-y-12 font-sans">
      
      {/* === STEP 1: Basic Info === */}
      <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 md:p-10 rounded-[2rem] transition-all hover:shadow-primary/5">
          <SectionTitle step="1" icon={Box} title="اطلاعات پایه محصول" desc="مشخصات عمومی و دسته‌بندی محصول را وارد کنید" />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-10">
              <div className="md:col-span-2 group">
                  <label className="block text-sm font-extrabold text-slate-800 mb-2 transition-colors group-focus-within:text-primary">نام محصول <span className="text-error">*</span></label>
                  <input 
                      {...register('shell.name')} 
                      className={clsx(underlineInputClass, "text-xl font-black py-4")}
                      placeholder="مثال: کارت ویزیت لمینت براق"
                  />
                  <FormError message={errors.shell?.name?.message} />
              </div>

              {/* دسته بندی - والد */}
              <div className="group">
                  <label className="block text-sm font-extrabold text-slate-800 mb-2 transition-colors group-focus-within:text-primary">۱. گروه اصلی</label>
                  <select 
                     className={clsx(underlineInputClass, "text-base font-bold text-slate-700 cursor-pointer")}
                     onChange={handleParentChange}
                     value={selectedParentId || ''}
                  >
                      <option value="" className="text-slate-400">-- انتخاب گروه --</option>
                      {parentCategories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
                  </select>
              </div>

              {/* دسته بندی - فرزند */}
              <div className="group relative">
                  <label className="block text-sm font-extrabold text-slate-800 mb-2 transition-colors group-focus-within:text-primary flex items-center gap-2">
                      ۲. زیر دسته (محصول نهایی) <span className="text-error">*</span>
                      {isLoadingChildren && <span className="loading loading-spinner loading-xs text-primary"></span>}
                  </label>
                  <select 
                     {...register('shell.category_id')} 
                     className={clsx(underlineInputClass, "text-base font-bold text-slate-700 cursor-pointer")}
                     disabled={!selectedParentId}
                  >
                      <option value="" className="text-slate-400">
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
              <div className="md:col-span-2 group">
                  <label className="block text-sm font-extrabold text-slate-800 mb-2 transition-colors group-focus-within:text-primary">توضیحات محصول</label>
                  <textarea 
                      {...register('shell.description')}
                      className="w-full bg-slate-50/50 border-b-2 border-slate-200 px-4 py-4 text-slate-800 placeholder-slate-400 focus:border-primary focus:bg-white focus:outline-none transition-all duration-300 rounded-t-2xl resize-none h-28"
                      placeholder="توضیحاتی که مشتری در صفحه محصول می‌بیند..."
                  ></textarea>
              </div>

              {/* تنظیمات اضافی */}
              <div className="md:col-span-2 bg-slate-50/80 p-6 rounded-2xl flex flex-col md:flex-row gap-8 items-end border border-slate-100/50">
                   <div className="w-full group">
                        <label className="block text-xs font-bold text-slate-500 mb-2">متن راهنما (مثل: زمان تحویل)</label>
                        <div className="flex gap-4 items-end">
                            <input {...register('shell.guide_text')} className={clsx(underlineInputClass, "flex-1")} placeholder="مثال: تحویل ۳ روز کاری"/>
                            <GuideTypeSelector register={register} name="shell.guide_type" />
                        </div>
                   </div>
                   <div className="min-w-[180px]">
                       <label className="cursor-pointer flex items-center gap-4 bg-white px-5 py-3 rounded-xl shadow-sm border border-slate-100 hover:border-primary/30 transition-all">
                           <input type="checkbox" {...register('shell.is_active')} className="toggle toggle-success toggle-md" />
                           <span className="font-bold text-slate-700 text-sm">محصول فعال</span>
                       </label>
                   </div>
              </div>
          </div>
      </div>

      {/* === STEP 2: Pricing Strategy === */}
      <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 md:p-10 rounded-[2rem] transition-all hover:shadow-primary/5">
          <SectionTitle step="2" icon={Calculator} title="استراتژی قیمت‌گذاری" desc="نحوه فروش و محاسبه قیمت برای این محصول" />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
               {/* کارت انتخاب تیراژی */}
               <div 
                  onClick={() => setValue('shell.has_quantity', true)}
                  className={clsx(
                      "cursor-pointer rounded-2xl p-6 border-2 transition-all duration-300 flex items-start gap-5 relative overflow-hidden group",
                      hasQuantity ? "border-primary bg-primary/5 shadow-md shadow-primary/10" : "border-slate-100 bg-white hover:border-slate-300 hover:bg-slate-50"
                  )}
               >
                   {hasQuantity && <div className="absolute top-0 right-0 w-16 h-16 bg-primary/10 rounded-bl-full -z-10 transition-transform group-hover:scale-150"></div>}
                   {hasQuantity && <CheckCircle2 size={24} className="absolute top-4 left-4 text-primary animate-in zoom-in" />}
                   
                   <div className={clsx("p-4 rounded-xl transition-colors", hasQuantity ? "bg-primary text-white shadow-lg shadow-primary/30" : "bg-slate-100 text-slate-400 group-hover:bg-slate-200")}>
                       <Printer size={28} />
                   </div>
                   <div className="pt-1">
                       <h4 className={clsx("font-black text-lg mb-1", hasQuantity ? "text-primary" : "text-slate-700")}>تیراژی (پکی)</h4>
                       <p className="text-sm text-slate-500 font-medium leading-relaxed">مثل کارت ویزیت یا تراکت (بسته‌های ۱۰۰۰تایی، ۲۰۰۰تایی)</p>
                   </div>
               </div>

               {/* کارت انتخاب تعدادی/متری */}
               <div 
                  onClick={() => setValue('shell.has_quantity', false)}
                  className={clsx(
                      "cursor-pointer rounded-2xl p-6 border-2 transition-all duration-300 flex items-start gap-5 relative overflow-hidden group",
                      !hasQuantity ? "border-emerald-500 bg-emerald-50/50 shadow-md shadow-emerald-500/10" : "border-slate-100 bg-white hover:border-slate-300 hover:bg-slate-50"
                  )}
               >
                   {!hasQuantity && <div className="absolute top-0 right-0 w-16 h-16 bg-emerald-500/10 rounded-bl-full -z-10 transition-transform group-hover:scale-150"></div>}
                   {!hasQuantity && <CheckCircle2 size={24} className="absolute top-4 left-4 text-emerald-500 animate-in zoom-in" />}

                   <div className={clsx("p-4 rounded-xl transition-colors", !hasQuantity ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/30" : "bg-slate-100 text-slate-400 group-hover:bg-slate-200")}>
                       <MousePointerClick size={28} />
                   </div>
                   <div className="pt-1">
                       <h4 className={clsx("font-black text-lg mb-1", !hasQuantity ? "text-emerald-700" : "text-slate-700")}>تعدادی / متری</h4>
                       <p className="text-sm text-slate-500 font-medium leading-relaxed">مثل بنر، استیکر یا کارهای سفارشی (تعداد دلخواه مشتری)</p>
                   </div>
               </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 p-8 rounded-[1.5rem] bg-gradient-to-br from-slate-50 to-white border border-slate-100/80 shadow-inner">
              <div className="group">
                  <label className="block text-sm font-extrabold text-slate-800 mb-3">قیمت پایه (تومان)</label>
                  <div className="relative flex items-center">
                      <input 
                          {...register('shell.price')}
                          className={clsx(underlineInputClass, "pl-12 font-mono text-2xl font-black text-emerald-600 dir-ltr")}
                          placeholder="0"
                      />
                      <DollarSign className="absolute left-2 text-emerald-400 group-focus-within:text-emerald-600 transition-colors" size={24}/>
                  </div>
                  <FormError message={errors.shell?.price?.message} />
              </div>

              {!hasQuantity && (
                  <div className="md:col-span-2 group">
                      <label className="block text-sm font-extrabold text-slate-800 mb-3">محدوده تعداد سفارش (حداقل و حداکثر)</label>
                      <div className="flex items-center gap-4">
                          <input type="number" {...register('pricing_config.min_quantity')} className={clsx(underlineInputClass, "text-center font-mono text-lg")} placeholder="حداقل (Min)"/>
                          <span className="text-slate-300 font-light">تا</span>
                          <input type="number" {...register('pricing_config.max_quantity')} className={clsx(underlineInputClass, "text-center font-mono text-lg")} placeholder="حداکثر (Max)"/>
                      </div>
                  </div>
              )}
          </div>

          <div className="mt-8 pt-6 flex flex-wrap items-center justify-between gap-6">
               <div className="flex items-center gap-4 bg-purple-50/50 px-5 py-3 rounded-2xl border border-purple-100">
                   <div className="p-2.5 bg-purple-100 text-purple-600 rounded-xl shadow-sm"><Palette size={20}/></div>
                   <h5 className="font-extrabold text-slate-800 text-sm">امکان سفارش طراحی آنلاین دارد؟</h5>
               </div>
               <div className="flex items-center gap-6 bg-white px-6 py-3 rounded-2xl shadow-sm border border-slate-100">
                   <input type="checkbox" {...register('pricing_config.design_service_available')} className="toggle toggle-primary toggle-md" />
                   {designAvailable && (
                       <div className="relative animate-in slide-in-from-right-4 fade-in">
                           <input type="number" {...register('pricing_config.design_fee')} className={clsx(underlineInputClass, "w-40 font-mono text-center text-primary font-bold")} placeholder="هزینه طراحی"/>
                       </div>
                   )}
               </div>
          </div>
      </div>

      {/* === STEP 3: Sizes & Quantities === */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          
          {/* Sizes */}
          <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 p-8 md:p-10 rounded-[2rem] border border-white hover:shadow-primary/5 transition-all flex flex-col h-full">
              <div className="flex justify-between items-start mb-6">
                  <SectionTitle step={hasQuantity ? "3" : "3"} icon={Ruler} title="سایزهای مجاز" desc="ابعاد قابل انتخاب برای مشتری" />
                  <button type="button" onClick={() => appendSize({ id: "", price_impact: 0 })} className="btn btn-primary btn-sm rounded-full shadow-lg shadow-primary/20 hover:scale-105 mt-2 px-6">
                     <Plus size={16}/> سایز جدید
                  </button>
              </div>
              <div className="space-y-4 flex-1">
                  {sizeFields.map((field, index) => (
                      <div key={field.id} className="p-5 bg-slate-50/80 rounded-2xl flex flex-col gap-4 relative group hover:bg-white hover:shadow-lg transition-all border border-transparent hover:border-slate-200">
                          <button onClick={() => removeSize(index)} className="absolute -top-3 -left-3 w-8 h-8 bg-error text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all shadow-md hover:scale-110"><Trash2 size={14}/></button>
                          
                          <div className="flex gap-5">
                              <select {...register(`sizes.${index}.id`)} className={clsx(underlineInputClass, "font-bold text-sm cursor-pointer")}>
                                  <option value="" className="text-slate-400">انتخاب سایز از سیستم...</option>
                                  {standardSizes.map(s => <option key={s.id} value={s.id}>{s.name} ({s.width}×{s.height})</option>)}
                              </select>
                              <div className="relative w-1/3">
                                  <input type="number" {...register(`sizes.${index}.price_impact`)} className={clsx(underlineInputClass, "font-mono text-emerald-600 font-bold pl-8")} placeholder="+ افزایش قیمت" />
                                  <span className="absolute left-1 top-3 text-[10px] text-slate-400">IQD</span>
                              </div>
                          </div>
                          
                          <div className="flex gap-4">
                              <input {...register(`sizes.${index}.guide_text`)} className={clsx(underlineInputClass, "text-xs")} placeholder="متن راهنمای این سایز (اختیاری)"/>
                              <GuideTypeSelector register={register} name={`sizes.${index}.guide_type`} />
                          </div>
                      </div>
                  ))}
                  {sizeFields.length === 0 && (
                      <div className="h-full min-h-[150px] flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-2xl bg-slate-50/50">
                          <Ruler size={32} className="mb-2 opacity-50"/>
                          <span className="text-sm font-medium">سایزی تعریف نشده است</span>
                      </div>
                  )}
              </div>
          </div>

          {/* Quantities */}
          {hasQuantity ? (
              <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 p-8 md:p-10 rounded-[2rem] border border-white hover:shadow-primary/5 transition-all flex flex-col h-full animate-in fade-in slide-in-from-bottom-4">
                  <div className="flex justify-between items-start mb-6">
                      <SectionTitle step="4" icon={Hash} title="تیراژهای مجاز" desc="تعدادهای قابل سفارش (پک)" />
                      <div className="w-48 mt-2 relative">
                           <select 
                                className="w-full bg-primary/10 text-primary border-none rounded-full px-4 py-2 font-bold text-sm cursor-pointer outline-none hover:bg-primary/20 transition-colors appearance-none text-center"
                                onChange={handleAddQuantity}
                           >
                               <option value="">+ افزودن تیراژ جدید...</option>
                               {systemQuantities.map((q) => (
                                   <option key={q.id} value={q.id}>{Number(q.value).toLocaleString()} عدد</option>
                               ))}
                           </select>
                      </div>
                  </div>

                  <div className="space-y-4 max-h-[450px] overflow-y-auto pr-2 custom-scrollbar flex-1">
                      {qtyFields.map((field, index) => {
                         const rowId = watch(`quantities.${index}.id`);
                         const foundQty = systemQuantities.find(q => String(q.id) === String(rowId));
                         const displayValue = foundQty ? Number(foundQty.value).toLocaleString() : '---';
                         
                         return (
                              <div key={field.id} className="p-5 bg-white border border-slate-100 rounded-2xl shadow-sm relative group hover:shadow-md hover:border-primary/30 transition-all">
                                  <button onClick={() => removeQty(index)} className="absolute top-1/2 -translate-y-1/2 left-4 w-8 h-8 text-slate-300 hover:bg-error hover:text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all"><Trash2 size={16}/></button>
                                  
                                  <div className="flex flex-col gap-3 pr-2">
                                      <span className="font-black text-2xl text-slate-800 tracking-tight">{displayValue} <span className="text-sm font-bold text-slate-400">عدد</span></span>
                                      
                                      <div className="flex gap-4 border-t border-slate-50 pt-3">
                                          <input {...register(`quantities.${index}.guide_text`)} className={clsx(underlineInputClass, "text-xs py-1")} placeholder="برچسب (مثل: پیشنهاد ویژه)"/>
                                          <GuideTypeSelector register={register} name={`quantities.${index}.guide_type`} />
                                      </div>
                                  </div>
                              </div>
                         );
                      })}
                      {qtyFields.length === 0 && (
                          <div className="h-full min-h-[150px] flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-2xl bg-slate-50/50">
                              <Hash size={32} className="mb-2 opacity-50"/>
                              <span className="text-sm font-medium">لیست تیراژ خالی است</span>
                          </div>
                      )}
                  </div>
              </div>
          ) : (
              <div className="hidden xl:block"></div> /* Empty div to keep grid layout clean if quantities are hidden */
          )}
      </div>

      {/* === Footer Actions (Glassmorphism) === */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex justify-center w-full px-6 pointer-events-none">
         <div className="bg-white/80 backdrop-blur-md p-3 rounded-full shadow-[0_20px_50px_-12px_rgba(0,0,0,0.15)] border border-white/50 pointer-events-auto">
             <button type="submit" disabled={isSaving} className="btn btn-primary h-14 px-12 rounded-full shadow-lg shadow-primary/40 text-lg font-black hover:scale-[1.02] active:scale-95 transition-all gap-3 border-none">
                {isSaving ? <span className="loading loading-spinner"></span> : <Save size={24}/>}
                {isEditMode ? 'ذخیره تغییرات' : 'ثبت و مرحله بعد'}
             </button>
         </div>
      </div>
    </form>
  );
};

export default ProductStep1Form;