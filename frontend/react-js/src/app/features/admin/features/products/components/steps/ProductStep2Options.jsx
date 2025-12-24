// src/app/features/admin/products/components/steps/ProductStep2Options.jsx
import React, { useState } from 'react';
import { useFieldArray, useForm } from 'react-hook-form';
import { 
  Settings, Plus, Trash2, GripVertical, CheckCircle2, 
  AlertCircle, ChevronDown, ChevronUp, Sparkles, DollarSign 
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
// فرض: سرویس دریافت لیست آپشن‌های گلوبال
// import { useAdminOptions } from '../../hooks/useAdminOptions'; 

const ProductStep2Options = ({ initialData, onSave, isSaving }) => {
  // استیت لوکال برای باز/بسته کردن آکاردئون هر آپشن
  const [expandedIndex, setExpandedIndex] = useState(null);

  const { register, control, handleSubmit, watch, formState: { errors } } = useForm({
    defaultValues: initialData || { options: [] }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "options"
  });

  // --- Handlers ---
  const handleAddSystemOption = () => {
    // افزودن یک ویژگی متصل به سیستم (خالی)
    append({ 
      option_id: "", // باید توسط کاربر انتخاب شود
      is_required: true, 
      values_config: [] 
    });
    setExpandedIndex(fields.length);
  };

  const handleAddCustomOption = () => {
    // افزودن یک ویژگی کاملاً اختصاصی
    append({ 
      option_id: null, 
      name: `custom_opt_${Date.now()}`,
      label: "",
      input_type: "select",
      is_required: true,
      values_config: [{ label: "پیش‌فرض", price_impact: 0 }] 
    });
    setExpandedIndex(fields.length);
  };

  const onSubmit = (data) => {
    // پاکسازی دیتا قبل از ارسال (حذف فیلدهای خالی و...)
    const cleanData = {
       options: data.options.map(opt => ({
          ...opt,
          // اگر آپشن سیستمی است، نام و لیبل دستی را حذف کن (چون از بانک می‌خواند)
          ...(opt.option_id ? { name: undefined, label: undefined } : {}) 
       }))
    };
    onSave(cleanData);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8 animate-in fade-in slide-in-from-bottom-4">
      
      {/* --- Header Section --- */}
      <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
           <h2 className="text-xl font-black text-slate-800 flex items-center gap-2">
             <Settings className="text-secondary" /> پیکربندی ویژگی‌ها
           </h2>
           <p className="text-slate-500 text-sm mt-1">
             مشخص کنید کاربر چه چیزهایی را می‌تواند انتخاب کند (رنگ، جنس، خدمات اضافه).
           </p>
        </div>
        
        <div className="flex gap-3">
           <button type="button" onClick={handleAddSystemOption} className="btn btn-outline border-slate-200 hover:bg-slate-50 text-slate-600 gap-2 rounded-xl">
             <Sparkles size={18}/> انتخاب از بانک ویژگی‌ها
           </button>
           <button type="button" onClick={handleAddCustomOption} className="btn btn-secondary text-white gap-2 rounded-xl shadow-lg shadow-secondary/20">
             <Plus size={18}/> ساخت ویژگی اختصاصی
           </button>
        </div>
      </div>

      {/* --- Options List --- */}
      <div className="space-y-4">
        {fields.length === 0 ? (
           <div className="text-center py-16 bg-white border-2 border-dashed border-slate-200 rounded-3xl">
              <div className="w-16 h-16 bg-slate-50 text-slate-300 rounded-full flex items-center justify-center mx-auto mb-4">
                 <Settings size={32}/>
              </div>
              <h3 className="text-lg font-bold text-slate-600">هنوز ویژگی‌ای اضافه نشده است</h3>
              <p className="text-slate-400 text-sm mt-1">برای شروع دکمه "انتخاب از بانک" یا "ساخت ویژگی" را بزنید.</p>
           </div>
        ) : (
          fields.map((field, index) => (
             <OptionItem 
                key={field.id}
                index={index}
                control={control}
                register={register}
                remove={remove}
                isExpanded={expandedIndex === index}
                onToggle={() => setExpandedIndex(expandedIndex === index ? null : index)}
                watch={watch}
                errors={errors}
             />
          ))
        )}
      </div>

      {/* --- Action Bar --- */}
      <div className="flex justify-end pt-6 border-t border-slate-200">
         <button 
            type="submit" 
            disabled={isSaving}
            className="btn btn-primary px-8 h-12 rounded-xl text-lg shadow-xl shadow-primary/20"
         >
            {isSaving ? <span className="loading loading-spinner"></span> : <CheckCircle2 size={20}/>}
            ذخیره ویژگی‌ها و رفتن به تصاویر
         </button>
      </div>

    </form>
  );
};

// --- Sub-Component: Single Option Row (The Complex Part) ---
const OptionItem = ({ index, control, register, remove, isExpanded, onToggle, watch, errors }) => {
  const isCustom = !watch(`options.${index}.option_id`); // اگر ID نداشت یعنی کاستوم است

  // Field Array برای مقادیر داخلی هر آپشن
  const { fields: valueFields, append: appendValue, remove: removeValue } = useFieldArray({
    control,
    name: `options.${index}.values_config`
  });

  return (
    <motion.div 
       layout 
       initial={{ opacity: 0, scale: 0.98 }}
       animate={{ opacity: 1, scale: 1 }}
       className={clsx(
         "bg-white border rounded-2xl overflow-hidden transition-all",
         isExpanded ? "border-primary ring-1 ring-primary/10 shadow-lg" : "border-slate-200 shadow-sm hover:border-slate-300"
       )}
    >
       {/* Header Row */}
       <div className="flex items-center gap-4 p-4 bg-slate-50/50 cursor-pointer select-none" onClick={onToggle}>
          <div className="cursor-grab text-slate-300 hover:text-slate-500"><GripVertical size={20}/></div>
          
          <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
             {/* Name / Selector */}
             <div>
                {isCustom ? (
                   <input 
                      {...register(`options.${index}.label`)}
                      placeholder="عنوان ویژگی (مثلاً: رنگ بندی)"
                      className="input input-sm input-ghost w-full font-bold text-slate-800 placeholder:font-normal"
                      onClick={(e) => e.stopPropagation()}
                   />
                ) : (
                   <select 
                      {...register(`options.${index}.option_id`)}
                      className="select select-sm select-ghost w-full font-bold text-slate-800"
                      onClick={(e) => e.stopPropagation()}
                   >
                      <option value="">انتخاب نوع ویژگی...</option>
                      <option value="1">جنس کاغذ (Global)</option>
                      <option value="2">نوع روکش (Global)</option>
                   </select>
                )}
             </div>

             {/* Badge */}
             <div className="hidden md:flex gap-2">
                <span className={clsx("badge badge-sm", isCustom ? "badge-secondary" : "badge-primary")}>
                   {isCustom ? "اختصاصی" : "سیستمی"}
                </span>
                {watch(`options.${index}.is_required`) && <span className="badge badge-sm badge-outline">اجباری</span>}
             </div>
          </div>

          <div className="flex items-center gap-2">
             <button type="button" onClick={(e) => { e.stopPropagation(); remove(index); }} className="btn btn-ghost btn-sm btn-square text-error">
                <Trash2 size={18}/>
             </button>
             <button type="button" className="btn btn-ghost btn-sm btn-square text-slate-400">
                {isExpanded ? <ChevronUp size={20}/> : <ChevronDown size={20}/>}
             </button>
          </div>
       </div>

       {/* Expanded Content */}
       <AnimatePresence>
         {isExpanded && (
           <motion.div 
             initial={{ height: 0, opacity: 0 }} 
             animate={{ height: "auto", opacity: 1 }} 
             exit={{ height: 0, opacity: 0 }}
             className="border-t border-slate-100"
           >
              <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-8">
                 
                 {/* Left: Configuration */}
                 <div className="space-y-4 lg:col-span-1 border-l border-slate-100 pl-6 order-last lg:order-first">
                    <h4 className="font-bold text-slate-700 text-sm">تنظیمات پایه</h4>
                    
                    <div className="form-control">
                       <label className="label cursor-pointer justify-start gap-3">
                          <input type="checkbox" {...register(`options.${index}.is_required`)} className="checkbox checkbox-sm checkbox-primary" />
                          <span className="label-text">انتخاب این گزینه اجباری باشد</span>
                       </label>
                    </div>

                    <div className="form-control">
                       <label className="label-text text-xs text-slate-500 mb-1">نوع نمایش</label>
                       <select {...register(`options.${index}.input_type`)} className="select select-bordered select-sm w-full rounded-lg">
                          <option value="select">لیست کشویی (Dropdown)</option>
                          <option value="radio">دکمه‌های رادیویی (Radio)</option>
                          <option value="checkbox">چند انتخابی (Checkbox)</option>
                       </select>
                    </div>

                    <div className="form-control">
                       <label className="label-text text-xs text-slate-500 mb-1">متن راهنما (Tooltip)</label>
                       <input {...register(`options.${index}.guide_text`)} className="input input-bordered input-sm w-full rounded-lg" placeholder="راهنمای مشتری..." />
                    </div>
                 </div>

                 {/* Right: Values Table */}
                 <div className="lg:col-span-2 space-y-4">
                    <div className="flex justify-between items-center">
                       <h4 className="font-bold text-slate-700 text-sm">مقادیر قابل انتخاب</h4>
                       <button type="button" onClick={() => appendValue({ label: "", price_impact: 0 })} className="btn btn-xs btn-ghost text-primary">
                          <Plus size={14}/> افزودن مقدار
                       </button>
                    </div>

                    <div className="overflow-x-auto bg-slate-50 rounded-xl border border-slate-200">
                       <table className="table table-sm w-full">
                          <thead className="text-xs text-slate-500 bg-slate-100">
                             <tr>
                                <th>عنوان مقدار</th>
                                <th>تأثیر قیمت (IQD)</th>
                                <th className="text-center">پیش‌فرض</th>
                                <th className="w-8"></th>
                             </tr>
                          </thead>
                          <tbody>
                             {valueFields.map((val, vIndex) => (
                                <tr key={val.id} className="group">
                                   <td>
                                      <input 
                                         {...register(`options.${index}.values_config.${vIndex}.label`)} 
                                         placeholder="مثلاً: قرمز"
                                         className="input input-ghost input-xs w-full font-medium" 
                                      />
                                   </td>
                                   <td>
                                      <div className="relative">
                                         <input 
                                            type="number" 
                                            {...register(`options.${index}.values_config.${vIndex}.price_impact`)} 
                                            className="input input-ghost input-xs w-full font-mono text-emerald-600 pl-6" 
                                            placeholder="0"
                                         />
                                         <DollarSign size={10} className="absolute left-1 top-1.5 text-slate-400"/>
                                      </div>
                                   </td>
                                   <td className="text-center">
                                      <input 
                                         type="checkbox" // توجه: برای رادیو باید منطق دستی بنویسی
                                         {...register(`options.${index}.values_config.${vIndex}.is_default`)} 
                                         className="radio radio-xs radio-primary" 
                                      />
                                   </td>
                                   <td>
                                      <button type="button" onClick={() => removeValue(vIndex)} className="btn btn-ghost btn-xs text-slate-400 hover:text-error opacity-0 group-hover:opacity-100 transition-opacity">
                                         <Trash2 size={14}/>
                                      </button>
                                   </td>
                                </tr>
                             ))}
                          </tbody>
                       </table>
                    </div>
                 </div>

              </div>
           </motion.div>
         )}
       </AnimatePresence>
    </motion.div>
  );
};

export default ProductStep2Options;