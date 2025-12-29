// src/app/features/admin/products/components/steps/ProductStep1Form.jsx
import React, { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { 
  Info, Box, Layers, ListPlus, Trash2, 
  Wand2, Calculator, Ruler, Hash, AlertTriangle, 
  Check, Save 
} from 'lucide-react';
import clsx from 'clsx';
import { useQuery } from '@tanstack/react-query';
import { ProductStep1Schema } from '../../schemas/productSchemas';
import { adminCategoryService } from '../../../../services/adminCategoryService';
// ✅ 1. اضافه شدن سرویس محصولات برای گرفتن سایزها
import { adminProductService } from '../../../../services/adminProductService';

// --- Helper Components ---
const SectionHeader = ({ icon: Icon, title, subtitle }) => (
  <div className="flex items-center gap-3 mb-6 border-b border-slate-100 pb-4">
    <div className="p-2 bg-primary/10 text-primary rounded-lg">
       <Icon size={20} />
    </div>
    <div>
      <h3 className="font-bold text-slate-800 text-lg">{title}</h3>
      <p className="text-xs text-slate-500">{subtitle}</p>
    </div>
  </div>
);

const FormError = ({ message }) => (
  message ? <span className="text-error text-xs mt-1 block animate-pulse font-medium flex items-center gap-1"><AlertTriangle size={10}/>{message}</span> : null
);

const ProductStep1Form = ({ initialData, onSave, isSaving, isEditMode }) => {
  
  // دریافت لیست دسته‌بندی‌ها
  const { data: categories = [] } = useQuery({
    queryKey: ['admin-categories-list'],
    queryFn: () => adminCategoryService.getAll(),
    staleTime: 1000 * 60 * 10,
  });

  // ✅ 2. دریافت لیست سایزهای استاندارد (Master Data)
  const { data: standardSizes = [] } = useQuery({
    queryKey: ['admin-standard-sizes'],
    // فرض بر این است که متد getStandardSizes را در سرویس اضافه کرده‌اید
    // اگر نه، موقتاً از یک آرایه خالی یا متد getAll استفاده کنید تا ارور ندهد
    queryFn: async () => {
        try { return await adminProductService.getStandardSizes(); } catch { return []; }
    },
    staleTime: 1000 * 60 * 30, 
  });

  const { register, control, handleSubmit, watch, setValue, formState: { errors } } = useForm({
    resolver: zodResolver(ProductStep1Schema),
    defaultValues: initialData || {
      shell: { has_quantity: true, is_active: true, guide_type: 'info' },
      pricing_config: { base_setup_price: 0, design_fee: 0 },
      quantities: [],
      sizes: []
    }
  });

  // Watchers
  const hasQuantity = watch('shell.has_quantity');
  
  // Field Arrays
  const { fields: qtyFields, append: appendQty, remove: removeQty } = useFieldArray({
    control, name: "quantities"
  });
  
  const { fields: sizeFields, append: appendSize, remove: removeSize } = useFieldArray({
    control, name: "sizes"
  });

  // Auto Slug Generator
  const generateSlug = () => {
    const name = watch('shell.name');
    if(name) {
       const slug = name.trim().toLowerCase()
         .replace(/\s+/g, '-')
         .replace(/[^\w\u0600-\u06FF-]/g, '');
       setValue('shell.slug', slug, { shouldValidate: true });
    }
  };

  const onSubmit = (data) => {
    onSave(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
      
      {/* === CARD 1: Basic Info === */}
      <div className="card bg-white shadow-sm border border-slate-200 p-6 rounded-2xl">
        <SectionHeader icon={Box} title="شناسنامه محصول" subtitle="اطلاعات اصلی جهت نمایش در فروشگاه" />
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="form-control">
            <label className="label text-sm font-bold text-slate-600">نام محصول <span className="text-error">*</span></label>
            <input 
              {...register('shell.name')} 
              placeholder="مثال: کارت ویزیت لمینت مات" 
              className="input input-bordered w-full rounded-xl focus:border-primary focus:ring-1 focus:ring-primary/20" 
            />
            <FormError message={errors.shell?.name?.message} />
          </div>

          <div className="form-control">
            <label className="label text-sm font-bold text-slate-600">دسته‌بندی <span className="text-error">*</span></label>
            <select 
              {...register('shell.category_id')} 
              className="select select-bordered w-full rounded-xl font-medium"
            >
              <option value="">انتخاب کنید...</option>
              {categories.map((cat) => (
                 <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
            <FormError message={errors.shell?.category?.message} />
          </div>

          <div className="form-control">
            <label className="label text-sm font-bold text-slate-600">لینک یکتا (Slug)</label>
            <div className="join w-full dir-ltr">
              <button type="button" onClick={generateSlug} className="btn btn-square join-item btn-ghost border-slate-300 text-slate-400 hover:text-primary" title="ساخت خودکار">
                 <Wand2 size={18}/>
              </button>
              <input 
                {...register('shell.slug')} 
                placeholder="product-unique-slug" 
                className="input input-bordered join-item w-full font-mono text-sm text-left" 
              />
            </div>
          </div>

          <div className="form-control">
            <label className="label text-sm font-bold text-slate-600">کد محصول (SKU)</label>
            <input 
               {...register('shell.code')} 
               placeholder="Auto Generated if empty"
               className="input input-bordered w-full rounded-xl font-mono"
            />
          </div>

          <div className="form-control md:col-span-2">
            <label className="label text-sm font-bold text-slate-600">توضیحات کوتاه</label>
            <textarea 
               {...register('shell.description')}
               className="textarea textarea-bordered h-24 rounded-xl text-base"
               placeholder="توضیحاتی درباره جنس، کیفیت و کاربرد محصول..."
            ></textarea>
          </div>
        </div>
      </div>

      {/* === CARD 2: Pricing Strategy === */}
      <div className="card bg-white shadow-sm border border-slate-200 p-6 rounded-2xl">
        <SectionHeader icon={Calculator} title="استراتژی فروش" subtitle="نحوه محاسبه قیمت و دریافت سفارش" />
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
           {/* Option 1: Offset */}
           <div 
              onClick={() => setValue('shell.has_quantity', true)}
              className={clsx(
                "cursor-pointer border-2 rounded-2xl p-4 transition-all hover:scale-[1.01] relative overflow-hidden select-none",
                hasQuantity ? "border-primary bg-primary/5" : "border-slate-100 bg-white hover:border-slate-200"
              )}
           >
              {hasQuantity && <div className="absolute top-0 right-0 bg-primary text-white p-1 rounded-bl-xl"><Check size={16}/></div>}
              <div className="flex items-center gap-3">
                 <div className={clsx("p-3 rounded-full", hasQuantity ? "bg-primary text-white" : "bg-slate-100 text-slate-400")}>
                    <Layers size={24}/>
                 </div>
                 <div>
                    <h4 className="font-bold text-lg text-slate-800">فروش بر اساس تیراژ (افست)</h4>
                    <p className="text-xs text-slate-500 mt-1">
                       انتخاب از بین تیراژهای مشخص (۱۰۰۰، ۲۰۰۰ و...)
                    </p>
                 </div>
              </div>
           </div>

           {/* Option 2: Digital */}
           <div 
              onClick={() => setValue('shell.has_quantity', false)}
              className={clsx(
                "cursor-pointer border-2 rounded-2xl p-4 transition-all hover:scale-[1.01] relative overflow-hidden select-none",
                !hasQuantity ? "border-secondary bg-secondary/5" : "border-slate-100 bg-white hover:border-slate-200"
              )}
           >
              {!hasQuantity && <div className="absolute top-0 right-0 bg-secondary text-white p-1 rounded-bl-xl"><Check size={16}/></div>}
              <div className="flex items-center gap-3">
                 <div className={clsx("p-3 rounded-full", !hasQuantity ? "bg-secondary text-white" : "bg-slate-100 text-slate-400")}>
                    <Ruler size={24}/>
                 </div>
                 <div>
                    <h4 className="font-bold text-lg text-slate-800">فروش متری/تعدادی (دیجیتال)</h4>
                    <p className="text-xs text-slate-500 mt-1">
                       ابعاد و تعداد دلخواه با فرمول محاسبه قیمت
                    </p>
                 </div>
              </div>
           </div>
        </div>

        {/* Pricing Config Fields */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 pt-6 border-t border-slate-100">
           <div className="form-control">
              <label className="label text-sm font-bold text-slate-600">هزینه ثابت اولیه</label>
              <div className="relative">
                 <input 
                    type="number" {...register('pricing_config.base_setup_price')}
                    className="input input-bordered w-full pl-10 font-mono rounded-xl"
                 />
                 <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs font-bold">IQD</span>
              </div>
           </div>
           
           <div className="form-control">
              <label className="label text-sm font-bold text-slate-600">هزینه طراحی (اختیاری)</label>
              <div className="relative">
                 <input 
                    type="number" {...register('pricing_config.design_fee')}
                    className="input input-bordered w-full pl-10 font-mono rounded-xl"
                 />
                 <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs font-bold">IQD</span>
              </div>
              <div className="flex items-center gap-2 mt-2">
                 <input type="checkbox" {...register('pricing_config.design_service_available')} className="checkbox checkbox-xs checkbox-primary" />
                 <span className="text-xs text-slate-500">فعال بودن خدمات طراحی</span>
              </div>
           </div>

           <div className="form-control">
              <label className="label text-sm font-bold text-slate-600">قیمت پایه نمایشی</label>
              <div className="relative">
                 <input 
                    type="number" {...register('shell.price')}
                    className="input input-bordered w-full pl-10 font-mono rounded-xl bg-slate-50"
                 />
                 <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs font-bold">IQD</span>
              </div>
           </div>
        </div>
      </div>

      {/* === CARD 3: Dynamic Tables === */}
      
      {/* A. QUANTITIES TABLE (Without Change) */}
      {hasQuantity && (
          <div className="card bg-white shadow-sm border border-slate-200 p-6 rounded-2xl animate-in fade-in slide-in-from-bottom-4">
             <div className="flex justify-between items-center mb-4">
                <SectionHeader icon={Hash} title="تیراژ و قیمت‌ها" subtitle="قیمت نهایی برای هر تیراژ مشخص" />
                <button type="button" onClick={() => appendQty({ value: 1000, price: 0 })} className="btn btn-sm btn-primary btn-outline gap-2 rounded-lg">
                   <ListPlus size={16}/> افزودن تیراژ
                </button>
             </div>
             
             {qtyFields.length === 0 ? (
                <div className="alert alert-warning text-sm bg-warning/10 border-warning/20">
                   <Info size={18}/> لطفا حداقل یک تیراژ (مثلاً ۱۰۰۰ عدد) اضافه کنید.
                </div>
             ) : (
                <div className="overflow-x-auto">
                   <table className="table table-sm w-full">
                      <thead>
                         <tr className="bg-slate-50 text-slate-500">
                            <th>تعداد</th>
                            <th>قیمت کل (IQD)</th>
                            <th>متن راهنما</th>
                            <th className="w-10"></th>
                         </tr>
                      </thead>
                      <tbody>
                         {qtyFields.map((field, index) => (
                            <tr key={field.id} className="group hover:bg-slate-50">
                               <td>
                                  <input type="number" {...register(`quantities.${index}.value`)} className="input input-bordered input-sm w-full font-mono" placeholder="1000" />
                                  <FormError message={errors.quantities?.[index]?.value?.message} />
                               </td>
                               <td>
                                  <input type="number" {...register(`quantities.${index}.price`)} className="input input-bordered input-sm w-full font-mono" placeholder="Price" />
                                  <FormError message={errors.quantities?.[index]?.price?.message} />
                               </td>
                               <td>
                                  <input type="text" {...register(`quantities.${index}.guide_text`)} className="input input-bordered input-sm w-full" placeholder="اختیاری" />
                               </td>
                               <td>
                                  <button type="button" onClick={() => removeQty(index)} className="btn btn-ghost btn-xs text-error opacity-50 group-hover:opacity-100"><Trash2 size={16}/></button>
                               </td>
                            </tr>
                         ))}
                      </tbody>
                   </table>
                </div>
             )}
             <FormError message={errors.quantities?.message || errors.quantities?.root?.message} />
          </div>
      )}

      {/* ✅ B. SIZES TABLE (اصلاح شده: انتخاب آیدی به جای تایپ نام) */}
      <div className="card bg-white shadow-sm border border-slate-200 p-6 rounded-2xl">
         <div className="flex justify-between items-center mb-4">
            <SectionHeader icon={Ruler} title="سایزهای استاندارد" subtitle="انتخاب سایزهای مجاز برای این محصول" />
            <button 
                type="button" 
                // ✅ مقدار پیش‌فرض باید شامل ID باشد نه name/width
                onClick={() => appendSize({ id: "", price_impact: 0 })} 
                className="btn btn-sm btn-secondary btn-outline gap-2 rounded-lg"
            >
               <ListPlus size={16}/> افزودن سایز
            </button>
         </div>

         {sizeFields.length === 0 ? (
             <div className="text-center py-8 bg-slate-50 rounded-xl border border-dashed border-slate-300">
                <p className="text-slate-400 text-sm">هیچ سایزی انتخاب نشده است.</p>
             </div>
         ) : (
            <div className="overflow-x-auto">
               <table className="table table-sm w-full">
                  <thead>
                     <tr className="bg-slate-50 text-slate-500">
                        <th className="w-1/2">انتخاب سایز استاندارد</th>
                        <th>افزایش قیمت (IQD)</th>
                        <th>توضیحات (اختیاری)</th>
                        <th className="w-10"></th>
                     </tr>
                  </thead>
                  <tbody>
                     {sizeFields.map((field, index) => {
                        // پیدا کردن سایز انتخاب شده برای نمایش ابعاد (فقط نمایشی)
                        const selectedSizeId = watch(`sizes.${index}.id`);
                        const selectedSizeInfo = standardSizes.find(s => String(s.id) === String(selectedSizeId));

                        return (
                           <tr key={field.id} className="group hover:bg-slate-50">
                              <td>
                                 <div className="flex flex-col">
                                    <select 
                                       {...register(`sizes.${index}.id`)} 
                                       className="select select-bordered select-sm w-full font-bold text-slate-700"
                                    >
                                       <option value="">انتخاب کنید...</option>
                                       {standardSizes.map(size => (
                                          <option key={size.id} value={size.id}>
                                             {size.name}
                                          </option>
                                       ))}
                                    </select>
                                    
                                    {/* نمایش ابعاد فقط برای اطلاع کاربر */}
                                    {selectedSizeInfo && (
                                       <span className="text-[10px] text-slate-400 mt-1 font-mono dir-ltr pl-1">
                                          ابعاد: {selectedSizeInfo.width} × {selectedSizeInfo.height} cm
                                       </span>
                                    )}
                                    <FormError message={errors.sizes?.[index]?.id?.message} />
                                 </div>
                              </td>
                              <td>
                                 <input 
                                    type="number"
                                    {...register(`sizes.${index}.price_impact`)}
                                    className="input input-bordered input-sm w-full font-mono text-emerald-600"
                                    placeholder="+0"
                                 />
                              </td>
                              <td>
                                 <input 
                                    type="text"
                                    {...register(`sizes.${index}.guide_text`)}
                                    className="input input-bordered input-sm w-full"
                                    placeholder="مثلاً: قالب خاص"
                                 />
                              </td>
                              <td>
                                 <button type="button" onClick={() => removeSize(index)} className="btn btn-ghost btn-xs text-error opacity-50 group-hover:opacity-100">
                                    <Trash2 size={16}/>
                                 </button>
                              </td>
                           </tr>
                        );
                     })}
                  </tbody>
               </table>
            </div>
         )}
      </div>

      {/* === ACTION BAR === */}
      <div className="flex justify-end gap-4 pt-4 border-t border-slate-200">
         <button type="button" className="btn btn-ghost text-slate-500">انصراف</button>
         <button 
            type="submit" 
            disabled={isSaving}
            className="btn btn-primary px-8 rounded-xl shadow-lg shadow-primary/30"
         >
            {isSaving ? <span className="loading loading-spinner"></span> : <Save size={18}/>}
            {isEditMode ? 'ذخیره تغییرات' : 'ثبت و ادامه (مرحله ۲)'}
         </button>
      </div>

    </form>
  );
};

export default ProductStep1Form;