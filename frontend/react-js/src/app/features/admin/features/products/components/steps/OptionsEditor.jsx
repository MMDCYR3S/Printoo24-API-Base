import React, { useState } from 'react';
import { useFormContext, useFieldArray, useWatch } from 'react-hook-form';
import { Settings, Plus, Trash2, GripVertical, ChevronDown, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import ValuesManager from './ValuesManager'; // فایلی که در مرحله بعد میسازیم

// استایل‌های مشترک اینپوت‌ها
const underlineInputClass = "w-full bg-transparent border-b-2 border-slate-200 px-2 py-3 text-slate-800 placeholder-slate-300 focus:border-primary focus:outline-none transition-all duration-300 hover:border-slate-300";
const underlineSelectClass = "w-full bg-transparent border-b-2 border-slate-200 px-2 py-3 text-slate-800 font-bold focus:border-primary focus:outline-none transition-all duration-300 cursor-pointer hover:border-slate-300";

// بج کمکی برای نمایش نوع ورودی
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

const OptionsEditor = () => {
    const [expandedIndex, setExpandedIndex] = useState(0);
    const { control } = useFormContext(); // دریافت کانتکست فرم بدون پراپ دریلینگ
    
    const { fields, append, remove } = useFieldArray({
        control,
        name: "options"
    });

    const handleAddOption = () => {
        append({
            product_option_id: null,
            label: "",
            name: `opt_${Math.random().toString(36).substr(2, 6)}`, // تولید نام یکتا
            input_type: "select",
            is_required: false,
            guide_text: "",
            values_config: []
        });
        setExpandedIndex(fields.length);
    };

    return (
        <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 rounded-[2rem]">
            {/* هدر بخش فرم‌ساز */}
            <div className="flex justify-between items-start mb-6">
                <div className="flex items-start gap-5">
                    <div className="w-14 h-14 rounded-[1.25rem] bg-gradient-to-br from-primary/10 to-primary/5 flex items-center justify-center text-primary shadow-sm border border-primary/10 relative">
                        <Settings size={26} strokeWidth={1.5} />
                        <div className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-primary text-white text-sm font-black flex items-center justify-center shadow-lg shadow-primary/40 border-2 border-white">3</div>
                    </div>
                    <div>
                        <h3 className="font-extrabold text-slate-800 text-2xl tracking-tight">طراحی فرم سفارش</h3>
                        <p className="text-sm text-slate-500 mt-2 font-medium">ویژگی‌ها و آپشن‌هایی که مشتری باید انتخاب کند را بسازید</p>
                    </div>
                </div>
                <button onClick={handleAddOption} type="button" className="btn btn-primary btn-sm rounded-full shadow-lg shadow-primary/20 hover:scale-105 px-6">
                    <Plus size={16}/> ویژگی جدید
                </button>
            </div>

            {/* لیست ویژگی‌ها */}
            <div className="space-y-5">
                {fields.map((field, index) => (
                    <OptionItem 
                        key={field.id}
                        index={index}
                        expanded={expandedIndex === index}
                        onToggle={() => setExpandedIndex(expandedIndex === index ? null : index)}
                        onRemove={() => remove(index)}
                    />
                ))}

                {/* وضعیت خالی */}
                {fields.length === 0 && (
                    <div className="flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-[2rem] bg-slate-50/50 py-16">
                        <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-sm mb-4">
                            <Sparkles className="text-primary/40" size={36}/>
                        </div>
                        <h4 className="font-extrabold text-slate-600 text-lg">هنوز ویژگی اضافه نکرده‌اید</h4>
                        <button onClick={handleAddOption} type="button" className="btn btn-outline btn-primary rounded-full px-8 mt-6">ساخت اولین ویژگی</button>
                    </div>
                )}
            </div>
        </div>
    );
};

// --- کامپوننت داخلی برای هر آیتم آکاردئون ---
const OptionItem = ({ index, expanded, onToggle, onRemove }) => {
    const { register, control } = useFormContext();
    const inputType = useWatch({ control, name: `options.${index}.input_type` });
    const label = useWatch({ control, name: `options.${index}.label` });
    const isRequired = useWatch({ control, name: `options.${index}.is_required` });

    return (
        <div className={clsx("bg-white border rounded-[1.5rem] transition-all duration-300", expanded ? "border-primary/30 shadow-xl shadow-primary/5 ring-4 ring-primary/5" : "border-slate-100 shadow-sm hover:border-slate-300")}>
            
            <input type="hidden" {...register(`options.${index}.product_option_id`)} />

            {/* هدر آکاردئون */}
            <div className="flex items-center gap-4 p-5 cursor-pointer rounded-t-[1.5rem]" onClick={onToggle}>
                <div className="cursor-grab text-slate-300 hover:text-slate-500 p-1"><GripVertical size={20}/></div>
                <div className="flex-1">
                    <h4 className="font-extrabold text-slate-800 text-lg">
                        {label || <span className="text-slate-400 italic">ویژگی بدون نام...</span>}
                    </h4>
                    <div className="flex items-center gap-2 mt-1.5">
                        <InputTypeBadge type={inputType} />
                        {isRequired && <span className="text-[10px] text-error bg-error/10 px-2 py-0.5 rounded-md font-bold shadow-sm">اجباری</span>}
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <button type="button" onClick={(e) => { e.stopPropagation(); onRemove(); }} className="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-error hover:bg-red-50 rounded-full transition-colors">
                        <Trash2 size={18}/>
                    </button>
                    <div className={clsx("w-8 h-8 flex items-center justify-center rounded-full bg-slate-50 text-slate-500 transition-transform duration-300", expanded && "rotate-180 bg-primary/10 text-primary")}>
                        <ChevronDown size={20}/>
                    </div>
                </div>
            </div>

            {/* بدنه آکاردئون */}
            <AnimatePresence>
                {expanded && (
                    <motion.div 
                        initial={{ height: 0, opacity: 0 }} 
                        animate={{ height: 'auto', opacity: 1 }} 
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                    >
                        <div className="border-t border-slate-100 p-6 space-y-8 bg-slate-50/30 rounded-b-[1.5rem]">
                            
                            {/* تنظیمات اصلی ویژگی */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div>
                                    <label className="block text-sm font-extrabold text-slate-800 mb-2">عنوان نمایشی (برای مشتری)</label>
                                    <input {...register(`options.${index}.label`)} className={underlineInputClass} placeholder="مثال: نوع روکش یا جنس کاغذ" />
                                </div>
                                <div>
                                    <label className="block text-sm font-extrabold text-slate-800 mb-2">نوع ورودی</label>
                                    <select {...register(`options.${index}.input_type`)} className={underlineSelectClass}>
                                        <option value="select">لیست کشویی (Dropdown)</option>
                                        <option value="radio">تک انتخابی (Radio)</option>
                                        <option value="checkbox">چند انتخابی (Checkbox)</option>
                                        <option value="text">متنی یک خطی (Text)</option>
                                        <option value="textarea">متنی چند خطی (Textarea)</option>
                                    </select>
                                </div>
                            </div>

                            {/* تنظیمات جانبی (اجباری بودن و متن راهنما) */}
                            <div className="flex flex-col md:flex-row gap-6 items-center bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                                <label className="cursor-pointer flex items-center gap-3 shrink-0">
                                    <input type="checkbox" {...register(`options.${index}.is_required`)} className="toggle toggle-error toggle-md"/>
                                    <span className="text-sm font-extrabold text-slate-700">پاسخ اجباری است</span>
                                </label>
                                <div className="hidden md:block h-8 w-px bg-slate-200"></div>
                                <div className="flex-1 w-full">
                                    <input {...register(`options.${index}.guide_text`)} className={underlineInputClass} placeholder="متن راهنما یا تول‌تیپ (اختیاری)"/>
                                </div>
                            </div>

                            {/* بخش مدیریت مقادیر و وابستگی‌ها (فقط برای اینپوت‌های انتخابی) */}
                            {(inputType === 'select' || inputType === 'radio' || inputType === 'checkbox') && (
                                <ValuesManager optionIndex={index} />
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default OptionsEditor;