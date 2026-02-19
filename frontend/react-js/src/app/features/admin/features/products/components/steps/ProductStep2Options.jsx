// src/app/features/admin/products/components/steps/ProductStep2Options.jsx
import React, { useState, useEffect, useMemo } from 'react';
import { useForm, useFieldArray, useWatch } from 'react-hook-form';
import { 
  Settings, Plus, Trash2, GripVertical, CheckCircle2, 
  ChevronDown, ChevronUp, Sparkles, DollarSign, Eye, Smartphone, Save, ListPlus
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import toast from 'react-hot-toast';

// --- Components Helper ---
const InputTypeIcon = ({ type }) => {
    switch(type) {
        case 'select': return <div className="badge badge-ghost badge-sm">لیست کشویی</div>;
        case 'radio': return <div className="badge badge-ghost badge-sm">تک انتخابی</div>;
        case 'checkbox': return <div className="badge badge-ghost badge-sm">چند انتخابی</div>;
        case 'text': return <div className="badge badge-ghost badge-sm">متنی</div>;
        default: return null;
    }
};

const ProductStep2Options = ({ initialData, onSave, isSaving }) => {
  const [expandedIndex, setExpandedIndex] = useState(0);

  // بررسی احتمال قوی: تبدیل کلیدهای بک‌اند (choices, type) به کلیدهای فرانت‌اند (values_config, input_type)
  const mappedInitialData = useMemo(() => {
    if (!initialData || !initialData.options) return { options: [] };
    
    return {
      ...initialData,
      options: initialData.options.map(opt => ({
        ...opt,
        // تبدیل type به input_type
        input_type: opt.type || opt.input_type || 'select',
        // تبدیل choices به values_config
        values_config: opt.choices || opt.values_config || []
      }))
    };
  }, [initialData]);

  const { register, control, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm({
    defaultValues: mappedInitialData
  });

  // اطمینان از اینکه اگر دیتای اولیه بعد از رندر اولیه تغییر کرد، فرم دوباره مقادیرش رو بشناسه
  useEffect(() => {
    if (initialData) {
      reset(mappedInitialData);
    }
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
       
       <div className="xl:col-span-7 space-y-6">
          <div className="flex justify-between items-center bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
             <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-50 text-purple-600 rounded-xl"><Settings size={24}/></div>
                <div>
                    <h3 className="font-bold text-slate-800">طراحی فرم سفارش</h3>
                    <p className="text-xs text-slate-500">سوالاتی که مشتری باید پاسخ دهد</p>
                </div>
             </div>
             <button onClick={handleAddOption} className="btn btn-primary btn-sm rounded-xl shadow-lg shadow-primary/20">
                <Plus size={16}/> افزودن ویژگی جدید
             </button>
          </div>

          <div className="space-y-4">
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
                   errors={errors}
                />
             ))}

             {fields.length === 0 && (
                <div className="text-center py-16 bg-white rounded-[2rem] border-2 border-dashed border-slate-200">
                    <Sparkles className="mx-auto text-slate-300 mb-4" size={48}/>
                    <h4 className="font-bold text-slate-600">هنوز ویژگی اضافه نکرده‌اید</h4>
                    <p className="text-xs text-slate-400 mt-2 mb-6">مثلاً: جنس کاغذ، نوع روکش، خدمات پس از چاپ</p>
                    <button onClick={handleAddOption} className="btn btn-outline btn-primary btn-sm rounded-xl">
                        ساخت اولین ویژگی
                    </button>
                </div>
             )}
          </div>
       </div>

       <div className="xl:col-span-5">
           <div className="sticky top-6">
               <div className="card bg-slate-800 text-white shadow-2xl rounded-[2.5rem] overflow-hidden border-4 border-slate-900">
                   <div className="bg-slate-900 p-4 flex justify-between items-center text-xs text-slate-400 border-b border-slate-700/50">
                       <span>9:41</span>
                       <div className="flex gap-1.5">
                          <div className="w-4 h-4 rounded-full bg-slate-700"></div>
                          <div className="w-4 h-4 rounded-full bg-slate-700"></div>
                       </div>
                   </div>

                   <div className="p-6 bg-slate-50 min-h-[500px] text-slate-800 relative">
                       <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-purple-500 to-secondary opacity-50"></div>
                       
                       <div className="mb-6 flex items-center gap-2 opacity-50">
                           <div className="w-12 h-12 bg-slate-200 rounded-xl"></div>
                           <div className="space-y-2">
                               <div className="w-32 h-3 bg-slate-200 rounded"></div>
                               <div className="w-20 h-2 bg-slate-200 rounded"></div>
                           </div>
                       </div>

                       <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2 text-sm">
                           <Settings size={16} className="text-primary"/> مشخصات سفارش
                       </h4>

                       <div className="space-y-5">
                           <LivePreview control={control} />
                       </div>

                       <div className="mt-8 pt-4 border-t border-slate-200 flex justify-between items-center opacity-50">
                           <div className="w-20 h-4 bg-slate-200 rounded"></div>
                           <div className="w-24 h-8 bg-slate-800 rounded-lg"></div>
                       </div>
                   </div>
                   
                   <div className="bg-slate-900 p-4 flex justify-center">
                       <div className="w-32 h-1 bg-slate-700 rounded-full"></div>
                   </div>
               </div>
               
               <div className="text-center mt-4 text-xs text-slate-400 flex items-center justify-center gap-2">
                   <Eye size={14}/> پیش‌نمایش زنده فرم مشتری
               </div>
           </div>
       </div>

       <div className="fixed bottom-6 left-6 z-50">
            <button 
                onClick={handleSubmit(onSave)}
                disabled={isSaving}
                className="btn btn-primary h-14 px-8 rounded-full shadow-2xl shadow-primary/40 text-lg font-bold"
            >
                {isSaving ? <span className="loading loading-spinner"></span> : <Save size={20}/>}
                ذخیره و نهایی‌سازی
            </button>
        </div>
    </div>
  );
};

// --- Sub-Component: Editor for Single Option ---
const OptionItemEditor = ({ index, expanded, onToggle, register, control, watch, remove, setValue, onLabelBlur, errors }) => {
    const inputType = watch(`options.${index}.input_type`);

    return (
        <div className={clsx("bg-white border transition-all rounded-2xl overflow-hidden", expanded ? "border-purple-300 shadow-lg ring-1 ring-purple-100" : "border-slate-200 hover:border-slate-300")}>
            
            {/* فیلد مخفی برای آیدی آپشن */}
            <input type="hidden" {...register(`options.${index}.id`)} />

            <div className="flex items-center gap-3 p-4 cursor-pointer bg-slate-50/50 hover:bg-slate-50" onClick={onToggle}>
                <div className="cursor-grab text-slate-300 hover:text-slate-500"><GripVertical size={16}/></div>
                <div className="flex-1">
                    <h4 className="font-bold text-slate-700 text-sm">
                        {watch(`options.${index}.label`) || <span className="text-slate-400 italic">ویژگی بدون نام...</span>}
                    </h4>
                    <div className="flex gap-2 mt-1">
                        <InputTypeIcon type={inputType} />
                        {watch(`options.${index}.is_required`) && <span className="text-[10px] text-error bg-error/10 px-1.5 rounded">اجباری</span>}
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button type="button" onClick={(e) => { e.stopPropagation(); remove(index); }} className="btn btn-xs btn-square btn-ghost text-error">
                        <Trash2 size={16}/>
                    </button>
                    {expanded ? <ChevronUp size={16} className="text-slate-400"/> : <ChevronDown size={16} className="text-slate-400"/>}
                </div>
            </div>

            <AnimatePresence>
                {expanded && (
                    <motion.div 
                        initial={{ height: 0, opacity: 0 }} 
                        animate={{ height: 'auto', opacity: 1 }} 
                        exit={{ height: 0, opacity: 0 }}
                        className="border-t border-slate-100 p-5 space-y-6 bg-white"
                    >
                        <div className="grid grid-cols-2 gap-4">
                            <div className="form-control">
                                <label className="label text-xs font-bold text-slate-600">عنوان نمایشی (برای مشتری)</label>
                                <input 
                                    {...register(`options.${index}.label`)} 
                                    onBlur={(e) => onLabelBlur(index, e.target.value)}
                                    className="input input-bordered w-full" 
                                    placeholder="مثال: نوع روکش"
                                />
                            </div>
                            <div className="form-control">
                                <label className="label text-xs font-bold text-slate-600">نوع ورودی</label>
                                <select {...register(`options.${index}.input_type`)} className="select select-bordered w-full font-mono text-xs">
                                    <option value="select">لیست کشویی (Dropdown)</option>
                                    <option value="radio">تک انتخابی (Radio)</option>
                                    <option value="checkbox">چند انتخابی (Checkbox)</option>
                                    <option value="text">متنی (Text)</option>
                                    <option value="textarea">متنی چند خطی</option>
                                </select>
                            </div>
                        </div>

                        <div className="flex gap-4 items-center bg-slate-50 p-3 rounded-xl border border-slate-100">
                             <div className="flex items-center gap-2">
                                 <input type="checkbox" {...register(`options.${index}.is_required`)} className="toggle toggle-xs toggle-error"/>
                                 <span className="text-xs font-bold text-slate-600">پاسخ اجباری است</span>
                             </div>
                             <div className="h-4 w-px bg-slate-300 mx-2"></div>
                             <div className="flex-1 flex gap-2 items-center">
                                 <input {...register(`options.${index}.guide_text`)} className="input input-xs input-bordered w-full bg-white" placeholder="متن راهنما (تول‌تیپ)"/>
                             </div>
                        </div>

                        {(inputType === 'select' || inputType === 'radio' || inputType === 'checkbox') && (
                            <OptionValuesManager 
                                nestIndex={index} 
                                control={control} 
                                register={register} 
                                watch={watch}
                            />
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

// --- Sub-Component: Values Manager (Inside Editor) ---
const OptionValuesManager = ({ nestIndex, control, register, watch }) => {
    const { fields, append, remove } = useFieldArray({
        control,
        name: `options.${nestIndex}.values_config`
    });

    return (
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
            <div className="flex justify-between items-center mb-3">
                <h5 className="font-bold text-xs text-slate-600 flex items-center gap-2">
                    <ListPlus size={14}/> مقادیر قابل انتخاب
                </h5>
                <button type="button" onClick={() => append({ id: null, label: "", price_impact: 0, is_default: false })} className="btn btn-xs btn-ghost text-primary">
                    <Plus size={12}/> سطر جدید
                </button>
            </div>

            <div className="space-y-2">
                {fields.map((item, k) => (
                    <div key={item.id} className="flex items-center gap-2 p-2 bg-white rounded-lg border border-slate-100 shadow-sm group">
                        
                        {/* فیلد مخفی برای آیدی مقادیر داخل لیست */}
                        <input type="hidden" {...register(`options.${nestIndex}.values_config.${k}.id`)} />

                        <GripVertical size={12} className="text-slate-300 cursor-grab"/>
                        
                        <input 
                            {...register(`options.${nestIndex}.values_config.${k}.label`)}
                            className="input input-xs input-bordered w-full focus:border-primary"
                            placeholder="عنوان گزینه (مثلاً: مات)"
                        />
                        
                        <div className="relative w-32 shrink-0">
                            <input 
                                type="number" 
                                {...register(`options.${nestIndex}.values_config.${k}.price_impact`)}
                                className={clsx(
                                    "input input-xs input-bordered w-full pl-6 font-mono text-right",
                                    watch(`options.${nestIndex}.values_config.${k}.price_impact`) > 0 ? "text-emerald-600 border-emerald-200 bg-emerald-50" : "text-slate-600"
                                )}
                                placeholder="0"
                            />
                            <span className="absolute left-1 top-0.5 text-[9px] text-slate-400">IQD</span>
                        </div>

                        <label className="cursor-pointer tooltip tooltip-left" data-tip="پیش‌فرض">
                            <input 
                                type="checkbox" 
                                {...register(`options.${nestIndex}.values_config.${k}.is_default`)}
                                className="checkbox checkbox-xs checkbox-primary rounded-md"
                            />
                        </label>

                        <button type="button" onClick={() => remove(k)} className="btn btn-xs btn-square btn-ghost text-error opacity-20 group-hover:opacity-100">
                            <Trash2 size={14}/>
                        </button>
                    </div>
                ))}
                {fields.length === 0 && <div className="text-center text-[10px] text-slate-400 py-2">هیچ گزینه ای تعریف نشده</div>}
            </div>
        </div>
    );
};

// --- Sub-Component: LIVE PREVIEW (The Customer View) ---
const LivePreview = ({ control }) => {
    const options = useWatch({ control, name: "options" });

    if (!options || options.length === 0) {
        return (
            <div className="text-center py-10 opacity-40">
                <Smartphone size={32} className="mx-auto mb-2"/>
                <p className="text-xs">فرم خالی است</p>
            </div>
        );
    }

    return (
        <div className="space-y-5">
            {options.map((opt, i) => (
                <div key={i} className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                    <label className="label py-0 mb-1.5">
                        <span className="label-text text-xs font-bold text-slate-700 flex items-center gap-1">
                            {opt.label || "نامشخص"}
                            {opt.is_required && <span className="text-error">*</span>}
                        </span>
                        {opt.guide_text && <span className="label-text-alt text-[10px] text-info bg-info/10 px-1 rounded">{opt.guide_text}</span>}
                    </label>

                    {opt.input_type === 'select' && (
                        <select className="select select-bordered select-sm w-full bg-white text-xs rounded-xl shadow-sm">
                            <option>انتخاب کنید...</option>
                            {opt.values_config?.map((val, idx) => (
                                <option key={idx}>
                                    {val.label} {val.price_impact > 0 ? `(+${Number(val.price_impact).toLocaleString()})` : ''}
                                </option>
                            ))}
                        </select>
                    )}

                    {opt.input_type === 'radio' && (
                        <div className="flex flex-col gap-2">
                            {opt.values_config?.map((val, idx) => (
                                <label key={idx} className="flex items-center gap-3 p-2 bg-white border border-slate-100 rounded-xl cursor-pointer hover:border-primary/50 transition-colors">
                                    <input type="radio" name={`preview_${i}`} className="radio radio-xs radio-primary" defaultChecked={val.is_default}/>
                                    <span className="text-xs flex-1 text-slate-600">{val.label || "گزینه خالی"}</span>
                                    {val.price_impact > 0 && <span className="text-[10px] font-mono text-emerald-600 bg-emerald-50 px-1 rounded">+{Number(val.price_impact).toLocaleString()}</span>}
                                </label>
                            ))}
                        </div>
                    )}

                    {opt.input_type === 'checkbox' && (
                         <div className="flex flex-col gap-2">
                            {opt.values_config?.map((val, idx) => (
                                <label key={idx} className="flex items-center gap-3 p-2 bg-white border border-slate-100 rounded-xl cursor-pointer hover:border-primary/50">
                                    <input type="checkbox" className="checkbox checkbox-xs checkbox-primary rounded-md" defaultChecked={val.is_default}/>
                                    <span className="text-xs flex-1 text-slate-600">{val.label || "گزینه خالی"}</span>
                                    {val.price_impact > 0 && <span className="text-[10px] font-mono text-emerald-600 bg-emerald-50 px-1 rounded">+{Number(val.price_impact).toLocaleString()}</span>}
                                </label>
                            ))}
                        </div>
                    )}
                    
                    {(opt.input_type === 'text' || opt.input_type === 'textarea') && (
                         <input disabled className="input input-sm input-bordered w-full bg-slate-50 text-xs" placeholder="محل تایپ مشتری..."/>
                    )}
                </div>
            ))}
            
            <div className="mt-8 pt-4 border-t border-dashed border-slate-300">
                <div className="flex justify-between items-center text-xs font-bold text-slate-700">
                    <span>جمع کل (تخمینی):</span>
                    <span className="font-mono text-lg text-primary">--- IQD</span>
                </div>
            </div>
        </div>
    );
};

export default ProductStep2Options;