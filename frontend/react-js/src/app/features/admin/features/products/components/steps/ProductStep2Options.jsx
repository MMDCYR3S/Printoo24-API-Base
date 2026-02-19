// src/app/features/admin/products/components/steps/ProductStep2Options.jsx
import React, { useState, useEffect, useMemo } from 'react';
import { useForm, useFieldArray, useWatch } from 'react-hook-form';
import { 
  Settings, Plus, Trash2, GripVertical, CheckCircle2, 
  ChevronDown, ChevronUp, Sparkles, DollarSign, Eye, Smartphone, Save, ListPlus , ImageIcon
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import toast from 'react-hot-toast';

// --- UI Helpers ---
const underlineInputClass = "w-full bg-transparent border-b-2 border-slate-200 px-2 py-3 text-slate-800 placeholder-slate-300 focus:border-primary focus:outline-none transition-all duration-300 hover:border-slate-300";
const underlineSelectClass = "w-full bg-transparent border-b-2 border-slate-200 px-2 py-3 text-slate-800 font-bold focus:border-primary focus:outline-none transition-all duration-300 cursor-pointer hover:border-slate-300";

const SectionTitle = ({ step, icon: Icon, title, desc }) => (
  <div className="flex items-start gap-5 mb-8 pb-6 border-b border-slate-200/60">
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

const InputTypeBadge = ({ type }) => {
    switch(type) {
        case 'select': return <span className="bg-blue-50 text-blue-600 border border-blue-100 px-2 py-0.5 rounded-md text-[10px] font-bold shadow-sm">لیست کشویی</span>;
        case 'radio': return <span className="bg-purple-50 text-purple-600 border border-purple-100 px-2 py-0.5 rounded-md text-[10px] font-bold shadow-sm">تک انتخابی</span>;
        case 'checkbox': return <span className="bg-emerald-50 text-emerald-600 border border-emerald-100 px-2 py-0.5 rounded-md text-[10px] font-bold shadow-sm">چند انتخابی</span>;
        case 'text': 
        case 'textarea': return <span className="bg-amber-50 text-amber-600 border border-amber-100 px-2 py-0.5 rounded-md text-[10px] font-bold shadow-sm">متنی</span>;
        default: return null;
    }
};

const ProductStep2Options = ({ initialData, onSave, isSaving }) => {
  const [expandedIndex, setExpandedIndex] = useState(0);

  // تبدیل کلیدهای بک‌اند (choices, type) به کلیدهای فرانت‌اند (values_config, input_type)
  const mappedInitialData = useMemo(() => {
    if (!initialData || !initialData.options) return { options: [] };
    
    return {
      ...initialData,
      options: initialData.options.map(opt => ({
        ...opt,
        input_type: opt.type || opt.input_type || 'select',
        values_config: opt.choices || opt.values_config || []
      }))
    };
  }, [initialData]);

  const { register, control, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm({
    defaultValues: mappedInitialData
  });

  useEffect(() => {
    if (initialData) reset(mappedInitialData);
  }, [mappedInitialData, reset]);

  const { fields, append, remove, move } = useFieldArray({
    control,
    name: "options"
  });

  const handleAddOption = () => {
    append({
      id: null,
      label: "",
      name: "", 
      input_type: "select",
      is_required: false,
      guide_text: "",
      guide_type: "info",
      values_config: []
    });
    setExpandedIndex(fields.length);
  };

  const handleLabelBlur = (index, value) => {
     const currentName = watch(`options.${index}.name`);
     if (!currentName && value) {
         const slug = "opt_" + Math.random().toString(36).substr(2, 6);
         setValue(`options.${index}.name`, slug);
     }
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 pb-32">
       
       {/* === LEFT: FORM BUILDER (7 Cols) === */}
       <div className="xl:col-span-7 flex flex-col gap-6">
          <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 rounded-[2rem]">
             <div className="flex justify-between items-start mb-2">
                 <SectionTitle step="3" icon={Settings} title="طراحی فرم سفارش" desc="ویژگی‌ها و آپشن‌هایی که مشتری باید انتخاب کند را بسازید" />
                 <button onClick={handleAddOption} type="button" className="btn btn-primary btn-sm rounded-full shadow-lg shadow-primary/20 hover:scale-105 mt-2 px-6">
                    <Plus size={16}/> ویژگی جدید
                 </button>
             </div>

             <div className="space-y-5">
                {fields.map((field, index) => (
                   <OptionItemEditor 
                      key={field.id}
                      index={index}
                      expanded={expandedIndex === index}
                      onToggle={() => setExpandedIndex(expandedIndex === index ? null : index)}
                      register={register}
                      control={control}
                      watch={watch}
                      remove={remove}
                      setValue={setValue}
                      onLabelBlur={handleLabelBlur}
                   />
                ))}

                {fields.length === 0 && (
                   <div className="flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-[2rem] bg-slate-50/50 py-16 hover:bg-slate-50 transition-colors">
                       <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-sm mb-4">
                           <Sparkles className="text-primary/40" size={36}/>
                       </div>
                       <h4 className="font-extrabold text-slate-600 text-lg">هنوز ویژگی اضافه نکرده‌اید</h4>
                       <p className="text-sm text-slate-400 mt-2 mb-6">مثلاً: جنس کاغذ، نوع روکش، خدمات پس از چاپ</p>
                       <button onClick={handleAddOption} type="button" className="btn btn-outline btn-primary rounded-full px-8">
                           ساخت اولین ویژگی
                       </button>
                   </div>
                )}
             </div>
          </div>
       </div>

       {/* === RIGHT: LIVE PREVIEW (5 Cols) === */}
       <div className="xl:col-span-5 relative">
           <div className="sticky top-32 pt-2">
               {/* Phone Mockup Frame */}
               <div className="mx-auto w-[320px] lg:w-[360px] h-[700px] bg-slate-900 border-[10px] border-slate-800 rounded-[3rem] shadow-2xl shadow-slate-900/40 relative overflow-hidden ring-1 ring-slate-700">
                   
                   {/* Phone Notch */}
                   <div className="absolute top-0 inset-x-0 h-6 bg-slate-800 rounded-b-2xl w-40 mx-auto z-50 flex justify-center items-center gap-2">
                       <div className="w-10 h-1.5 bg-slate-900 rounded-full"></div>
                       <div className="w-2 h-2 bg-slate-900 rounded-full"></div>
                   </div>

                   {/* Phone Status Bar */}
                   <div className="absolute top-0 inset-x-0 h-8 px-5 flex justify-between items-center z-40 text-[10px] text-slate-800 font-medium">
                       <span>9:41</span>
                       <div className="flex gap-1">
                          <div className="w-3 h-3 rounded-full bg-slate-800"></div>
                          <div className="w-3 h-3 rounded-full bg-slate-800"></div>
                       </div>
                   </div>

                   {/* Phone Screen Content */}
                   <div className="w-full h-full bg-[#f8fafc] overflow-y-auto custom-scrollbar pt-12 pb-8 relative">
                       {/* App Header Simulation */}
                       <div className="px-6 mb-4 pb-6 border-b border-slate-200/60">
                           <div className="w-16 h-16 bg-white shadow-sm rounded-2xl mb-4 flex items-center justify-center">
                               <ImageIcon className="text-slate-300" size={28}/>
                           </div>

                       </div>

                       {/* The Actual Live Form */}
                       <div className="px-6 space-y-6">
                           <h4 className="font-extrabold text-slate-800 flex items-center gap-2 text-sm border-r-4 border-primary pr-2">
                               مشخصات سفارش
                           </h4>
                           <LivePreview control={control} />
                       </div>
                   </div>
                   
                   {/* Phone Home Indicator */}
                   <div className="absolute bottom-2 inset-x-0 flex justify-center z-50 pointer-events-none">
                       <div className="w-24 h-1 bg-slate-300/50 rounded-full"></div>
                   </div>
               </div>
               
               <div className="text-center mt-6 text-sm font-bold text-slate-400 flex items-center justify-center gap-2 bg-white/50 py-2 rounded-full w-max mx-auto px-6 shadow-sm border border-white">
                   <Eye size={18} className="text-primary"/> پیش‌نمایش زنده در موبایل
               </div>
           </div>
       </div>

       {/* Footer Action */}
       <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex justify-center w-full px-6 pointer-events-none">
         <div className="bg-white/80 backdrop-blur-md p-3 rounded-full shadow-[0_20px_50px_-12px_rgba(0,0,0,0.15)] border border-white/50 pointer-events-auto">
             <button type="submit" onClick={handleSubmit(onSave)} disabled={isSaving} className="btn btn-primary h-14 px-12 rounded-full shadow-lg shadow-primary/40 text-lg font-black hover:scale-[1.02] active:scale-95 transition-all gap-3 border-none">
                {isSaving ? <span className="loading loading-spinner"></span> : <Save size={24}/>}
                ذخیره و نهایی‌سازی
             </button>
         </div>
      </div>

    </div>
  );
};

// --- Sub-Component: Editor for Single Option ---
const OptionItemEditor = ({ index, expanded, onToggle, register, control, watch, remove, setValue, onLabelBlur }) => {
    const inputType = watch(`options.${index}.input_type`);

    return (
        <div className={clsx(
            "bg-white border rounded-[1.5rem] transition-all duration-300", 
            expanded ? "border-primary/30 shadow-xl shadow-primary/5 ring-4 ring-primary/5" : "border-slate-100 shadow-sm hover:border-slate-300 hover:shadow-md"
        )}>
            
            <input type="hidden" {...register(`options.${index}.id`)} />

            {/* Header */}
            <div className="flex items-center gap-4 p-5 cursor-pointer rounded-t-[1.5rem]" onClick={onToggle}>
                <div className="cursor-grab text-slate-300 hover:text-slate-500 p-1"><GripVertical size={20}/></div>
                <div className="flex-1">
                    <h4 className="font-extrabold text-slate-800 text-lg">
                        {watch(`options.${index}.label`) || <span className="text-slate-400 italic">ویژگی بدون نام...</span>}
                    </h4>
                    <div className="flex items-center gap-2 mt-1.5">
                        <InputTypeBadge type={inputType} />
                        {watch(`options.${index}.is_required`) && <span className="text-[10px] text-error bg-error/10 px-2 py-0.5 rounded-md font-bold shadow-sm">اجباری</span>}
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <button type="button" onClick={(e) => { e.stopPropagation(); remove(index); }} className="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-error hover:bg-red-50 rounded-full transition-colors">
                        <Trash2 size={18}/>
                    </button>
                    <div className={clsx("w-8 h-8 flex items-center justify-center rounded-full bg-slate-50 text-slate-500 transition-transform duration-300", expanded && "rotate-180 bg-primary/10 text-primary")}>
                        <ChevronDown size={20}/>
                    </div>
                </div>
            </div>

            {/* Body */}
            <AnimatePresence>
                {expanded && (
                    <motion.div 
                        initial={{ height: 0, opacity: 0 }} 
                        animate={{ height: 'auto', opacity: 1 }} 
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                    >
                        <div className="border-t border-slate-100 p-6 md:p-8 space-y-8 bg-slate-50/30 rounded-b-[1.5rem]">
                            
                            {/* Row 1: Config */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="group">
                                    <label className="block text-sm font-extrabold text-slate-800 mb-2 transition-colors group-focus-within:text-primary">عنوان نمایشی (برای مشتری)</label>
                                    <input 
                                        {...register(`options.${index}.label`)} 
                                        onBlur={(e) => onLabelBlur(index, e.target.value)}
                                        className={underlineInputClass} 
                                        placeholder="مثال: نوع روکش یا جنس کاغذ"
                                    />
                                </div>
                                <div className="group">
                                    <label className="block text-sm font-extrabold text-slate-800 mb-2 transition-colors group-focus-within:text-primary">نوع ورودی</label>
                                    <select {...register(`options.${index}.input_type`)} className={underlineSelectClass}>
                                        <option value="select">لیست کشویی (Dropdown)</option>
                                        <option value="radio">تک انتخابی (Radio)</option>
                                        <option value="checkbox">چند انتخابی (Checkbox)</option>
                                        <option value="text">متنی یک خطی (Text)</option>
                                        <option value="textarea">متنی چند خطی (Textarea)</option>
                                    </select>
                                </div>
                            </div>

                            {/* Row 2: Settings */}
                            <div className="flex flex-col md:flex-row gap-6 items-center bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                                 <label className="cursor-pointer flex items-center gap-3 shrink-0">
                                     <input type="checkbox" {...register(`options.${index}.is_required`)} className="toggle toggle-error toggle-md"/>
                                     <span className="text-sm font-extrabold text-slate-700">پاسخ اجباری است</span>
                                 </label>
                                 <div className="hidden md:block h-8 w-px bg-slate-200"></div>
                                 <div className="flex-1 w-full group">
                                     <input {...register(`options.${index}.guide_text`)} className={underlineInputClass} placeholder="متن راهنما یا تول‌تیپ (اختیاری)"/>
                                 </div>
                            </div>

                            {/* Row 3: Values Manager */}
                            {(inputType === 'select' || inputType === 'radio' || inputType === 'checkbox') && (
                                <OptionValuesManager 
                                    nestIndex={index} 
                                    control={control} 
                                    register={register} 
                                    watch={watch}
                                />
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

// --- Sub-Component: Values Manager ---
const OptionValuesManager = ({ nestIndex, control, register, watch }) => {
    const { fields, append, remove } = useFieldArray({
        control,
        name: `options.${nestIndex}.values_config`
    });

    return (
        <div className="bg-white rounded-3xl p-6 md:p-8 border border-slate-200 shadow-sm">
            <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-sm">
                       <ListPlus size={20}/>
                    </div>
                    <div>
                        <h5 className="font-extrabold text-slate-800 text-base">مقادیر قابل انتخاب</h5>
                        <p className="text-xs text-slate-400 font-medium">گزینه‌هایی که مشتری می‌بیند</p>
                    </div>
                </div>
                <button type="button" onClick={() => append({ id: null, label: "", price_impact: 0, is_default: false })} className="btn btn-sm btn-primary btn-outline rounded-full px-5">
                    <Plus size={14}/> گزینه جدید
                </button>
            </div>

            <div className="space-y-3">
                {fields.map((item, k) => (
                    <div key={item.id} className="flex flex-col sm:flex-row items-center gap-4 p-4 bg-slate-50/80 rounded-2xl border border-slate-100 shadow-sm group hover:bg-white hover:border-slate-200 transition-all hover:shadow-md relative overflow-hidden">
                        
                        <input type="hidden" {...register(`options.${nestIndex}.values_config.${k}.id`)} />
                        
                        {/* Delete Button (Hover) */}
                        <button type="button" onClick={() => remove(k)} className="absolute top-0 right-0 h-full w-12 bg-error text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all translate-x-full group-hover:translate-x-0 z-10">
                            <Trash2 size={18}/>
                        </button>

                        <GripVertical size={16} className="text-slate-300 cursor-grab shrink-0"/>
                        
                        {/* Label */}
                        <div className="flex-1 w-full relative z-20 bg-transparent">
                            <input 
                                {...register(`options.${nestIndex}.values_config.${k}.label`)}
                                className={clsx(underlineInputClass, "py-2 text-sm font-bold bg-transparent")}
                                placeholder="عنوان گزینه (مثلاً: سلفون مات)"
                            />
                        </div>
                        
                        {/* Price */}
                        <div className="relative w-full sm:w-40 shrink-0 z-20 bg-transparent">
                            <input 
                                type="number" 
                                {...register(`options.${nestIndex}.values_config.${k}.price_impact`)}
                                className={clsx(
                                    underlineInputClass, 
                                    "py-2 font-mono text-sm pl-8 text-left dir-ltr bg-transparent",
                                    watch(`options.${nestIndex}.values_config.${k}.price_impact`) > 0 ? "text-emerald-600 font-black border-emerald-300" : "text-slate-600 font-bold"
                                )}
                                placeholder="0"
                            />
                            <span className="absolute left-1 top-3 text-[10px] font-bold text-slate-400">IQD</span>
                        </div>

                        {/* Default Checkbox */}
                        <label className="cursor-pointer flex items-center gap-2 z-20 px-2">
                            <input 
                                type="checkbox" 
                                {...register(`options.${nestIndex}.values_config.${k}.is_default`)}
                                className="checkbox checkbox-sm checkbox-primary rounded-md border-slate-300"
                            />
                            <span className="text-[10px] font-bold text-slate-500 whitespace-nowrap">پیش‌فرض</span>
                        </label>
                    </div>
                ))}
                {fields.length === 0 && (
                    <div className="text-center py-8 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
                        <span className="text-xs font-bold text-slate-400">هیچ گزینه‌ای تعریف نشده است</span>
                    </div>
                )}
            </div>
        </div>
    );
};

// --- Sub-Component: LIVE PREVIEW ---
const LivePreview = ({ control }) => {
    const options = useWatch({ control, name: "options" });

    if (!options || options.length === 0) {
        return (
            <div className="text-center py-16 opacity-30 flex flex-col items-center">
                <Smartphone size={48} className="mb-4 text-slate-400"/>
                <p className="text-sm font-bold text-slate-500">مشتری اینجا فرم را می‌بیند</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {options.map((opt, i) => (
                <div key={i} className="animate-in fade-in slide-in-from-bottom-2 duration-300 bg-white p-5 rounded-3xl shadow-sm border border-slate-100">
                    <label className="block mb-3">
                        <span className="text-sm font-extrabold text-slate-800 flex items-center gap-1.5">
                            {opt.label || "نامشخص"}
                            {opt.is_required && <span className="text-error text-lg leading-none">*</span>}
                        </span>
                        {opt.guide_text && <span className="block text-[10px] font-bold text-slate-500 mt-1">{opt.guide_text}</span>}
                    </label>

                    {opt.input_type === 'select' && (
                        <div className="relative">
                            <select className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-xs font-bold rounded-xl px-3 py-3 appearance-none focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-sm">
                                <option>انتخاب کنید...</option>
                                {opt.values_config?.map((val, idx) => (
                                    <option key={idx}>
                                        {val.label} {val.price_impact > 0 ? `(+${Number(val.price_impact).toLocaleString()})` : ''}
                                    </option>
                                ))}
                            </select>
                            <ChevronDown size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"/>
                        </div>
                    )}

                    {opt.input_type === 'radio' && (
                        <div className="flex flex-col gap-2.5">
                            {opt.values_config?.map((val, idx) => (
                                <label key={idx} className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-xl cursor-pointer hover:border-primary/50 hover:bg-slate-50 transition-colors shadow-sm">
                                    <input type="radio" name={`preview_${i}`} className="radio radio-xs radio-primary" defaultChecked={val.is_default}/>
                                    <span className="text-xs font-bold text-slate-700 flex-1">{val.label || "گزینه خالی"}</span>
                                    {val.price_impact > 0 && <span className="text-[10px] font-mono text-emerald-600 font-black bg-emerald-50 px-2 py-1 rounded-md">+{Number(val.price_impact).toLocaleString()}</span>}
                                </label>
                            ))}
                        </div>
                    )}

                    {opt.input_type === 'checkbox' && (
                         <div className="flex flex-col gap-2.5">
                            {opt.values_config?.map((val, idx) => (
                                <label key={idx} className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-xl cursor-pointer hover:border-primary/50 hover:bg-slate-50 transition-colors shadow-sm">
                                    <input type="checkbox" className="checkbox checkbox-xs checkbox-primary rounded-md" defaultChecked={val.is_default}/>
                                    <span className="text-xs font-bold text-slate-700 flex-1">{val.label || "گزینه خالی"}</span>
                                    {val.price_impact > 0 && <span className="text-[10px] font-mono text-emerald-600 font-black bg-emerald-50 px-2 py-1 rounded-md">+{Number(val.price_impact).toLocaleString()}</span>}
                                </label>
                            ))}
                        </div>
                    )}
                    
                    {(opt.input_type === 'text' || opt.input_type === 'textarea') && (
                         <input disabled className="w-full bg-slate-50 border border-slate-200 text-slate-400 text-xs font-bold rounded-xl px-3 py-3" placeholder="محل تایپ مشتری..."/>
                    )}
                </div>
            ))}
            
            <div className="mt-8 pt-6 border-t border-slate-200/60">
                <div className="flex justify-between items-center bg-emerald-50 text-emerald-700 p-4 rounded-2xl border border-emerald-100">
                    <span className="text-xs font-extrabold">جمع کل (تخمینی)</span>
                    <span className="font-mono text-lg font-black tracking-tight">--- IQD</span>
                </div>
            </div>
        </div>
    );
};

export default ProductStep2Options;