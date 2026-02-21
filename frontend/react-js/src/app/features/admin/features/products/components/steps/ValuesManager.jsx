import React, { useState } from 'react';
import { useFormContext, useFieldArray, useWatch } from 'react-hook-form';
import { Plus, Trash2, GripVertical, Settings2, ListPlus, Link2, Calculator } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import { generateRefId } from '../../../../hooks/useStep2Form';

const underlineInputClass = "w-full bg-transparent border-b-2 border-slate-200 px-2 py-2 text-slate-800 focus:border-primary focus:outline-none transition-all duration-300";

const ValuesManager = ({ optionIndex }) => {
    const { control } = useFormContext();
    const { fields, append, remove } = useFieldArray({
        control,
        name: `options.${optionIndex}.values_config`
    });

    const handleAddValue = () => {
        append({
            id: null,
            ref_id: generateRefId('val'), // شناسه موقت برای برقراری وابستگی‌ها
            label: "",
            price_impact: 0,
            is_default: false,
            conditions: [],
            quantity_prices: []
        });
    };

    return (
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm mt-6">
            <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-sm">
                        <ListPlus size={20}/>
                    </div>
                    <div>
                        <h5 className="font-extrabold text-slate-800 text-base">مقادیر و تنظیمات پیشرفته</h5>
                        <p className="text-xs text-slate-400 font-medium">گزینه‌ها، قیمت‌گذاری تیراژ و وابستگی‌ها</p>
                    </div>
                </div>
                <button type="button" onClick={handleAddValue} className="btn btn-sm btn-primary btn-outline rounded-full px-5">
                    <Plus size={14}/> افزودن گزینه
                </button>
            </div>

            <div className="space-y-4">
                {fields.map((item, valueIndex) => (
                    <ValueRow 
                        key={item.id} 
                        optionIndex={optionIndex} 
                        valueIndex={valueIndex} 
                        remove={() => remove(valueIndex)} 
                    />
                ))}
                
                {fields.length === 0 && (
                    <div className="text-center py-8 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
                        <span className="text-xs font-bold text-slate-400">هیچ گزینه‌ای برای این ویژگی تعریف نشده است</span>
                    </div>
                )}
            </div>
        </div>
    );
};

// --- کامپوننت داخلی: یک سطر از مقادیر به همراه تنظیمات پیشرفته ---
const ValueRow = ({ optionIndex, valueIndex, remove }) => {
    const [showAdvanced, setShowAdvanced] = useState(false);
    const { register, control } = useFormContext();
    
    // گرفتن مقادیر برای استایل‌دهی در لحظه
    const price = useWatch({ control, name: `options.${optionIndex}.values_config.${valueIndex}.price_impact` });
    
    return (
        <div className="flex flex-col bg-slate-50/80 rounded-2xl border border-slate-100 shadow-sm group hover:bg-white hover:border-slate-200 transition-all relative">
            
            {/* شناسه مخفی برای بک‌اند */}
            <input type="hidden" {...register(`options.${optionIndex}.values_config.${valueIndex}.id`)} />
            <input type="hidden" {...register(`options.${optionIndex}.values_config.${valueIndex}.ref_id`)} />

            {/* بخش اصلی سطر (همیشه نمایان) */}
            <div className="flex flex-col sm:flex-row items-center gap-4 p-4 relative overflow-hidden z-10">
                <button type="button" onClick={remove} className="absolute top-0 right-0 h-full w-10 bg-error text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all translate-x-full group-hover:translate-x-0 z-20">
                    <Trash2 size={16}/>
                </button>

                <GripVertical size={16} className="text-slate-300 cursor-grab shrink-0"/>
                
                <div className="flex-1 w-full relative z-20">
                    <input 
                        {...register(`options.${optionIndex}.values_config.${valueIndex}.label`)}
                        className={clsx(underlineInputClass, "text-sm font-bold")}
                        placeholder="عنوان گزینه (مثلاً: سلفون مات)"
                    />
                </div>
                
                <div className="relative w-full sm:w-36 shrink-0 z-20">
                    <input 
                        type="number" 
                        {...register(`options.${optionIndex}.values_config.${valueIndex}.price_impact`)}
                        className={clsx(underlineInputClass, "font-mono text-sm pl-8 text-left dir-ltr", price > 0 ? "text-emerald-600 font-black" : "text-slate-600 font-bold")}
                        placeholder="0"
                    />
                    <span className="absolute left-1 top-3 text-[10px] font-bold text-slate-400">IQD</span>
                </div>

                <label className="cursor-pointer flex items-center gap-2 z-20 px-2 shrink-0">
                    <input type="checkbox" {...register(`options.${optionIndex}.values_config.${valueIndex}.is_default`)} className="checkbox checkbox-sm checkbox-primary rounded-md"/>
                    <span className="text-[10px] font-bold text-slate-500">پیش‌فرض</span>
                </label>

                <button 
                    type="button" 
                    onClick={() => setShowAdvanced(!showAdvanced)} 
                    className={clsx("btn btn-xs rounded-md z-20 shrink-0 border-none transition-colors", showAdvanced ? "bg-primary/10 text-primary" : "bg-slate-200 text-slate-600")}
                >
                    <Settings2 size={14}/> پیشرفته
                </button>
            </div>

            {/* بخش تنظیمات پیشرفته (وابستگی‌ها و قیمت تیراژ) */}
            <AnimatePresence>
                {showAdvanced && (
                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                        <div className="p-5 border-t border-slate-200 bg-slate-100/50 rounded-b-2xl grid grid-cols-1 xl:grid-cols-2 gap-6">
                            
                            {/* ستون راست: شروط و وابستگی‌ها */}
                            <ConditionManager optionIndex={optionIndex} valueIndex={valueIndex} />

                            {/* ستون چپ: ماتریس قیمت تیراژ */}
                            <QuantityPriceManager optionIndex={optionIndex} valueIndex={valueIndex} />

                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

// --- کامپوننت مدیریت شروط (وابستگی به سایر ویژگی‌ها) ---
const ConditionManager = ({ optionIndex, valueIndex }) => {
    const { control, register } = useFormContext();
    const allOptions = useWatch({ control, name: 'options' }) || [];
    
    const { fields: condFields, append: appendCond, remove: removeCond } = useFieldArray({
        control,
        name: `options.${optionIndex}.values_config.${valueIndex}.conditions`
    });

    // استخراج تمام مقادیر از سایر ویژگی‌ها برای لیست کشویی شروط
    const availableDependencies = allOptions.reduce((acc, opt, idx) => {
        if (idx === optionIndex) return acc; // ویژگی فعلی را در لیست شروط نمی‌آوریم
        const values = opt.values_config || [];
        values.forEach(val => {
            if (val.label) {
                acc.push({ optLabel: opt.label, valLabel: val.label, ref: val.ref_id || val.id });
            }
        });
        return acc;
    }, []);

    return (
        <div className="bg-white p-4 rounded-xl border border-slate-200">
            <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-extrabold text-slate-700 flex items-center gap-1.5"><Link2 size={14} className="text-primary"/> شروط نمایش (وابستگی)</span>
                <button type="button" onClick={() => appendCond({ required_ref_id: "", action: "show" })} className="text-[10px] text-primary font-bold hover:underline">+ افزودن شرط</button>
            </div>
            
            <div className="space-y-2">
                {condFields.map((cond, k) => (
                    <div key={cond.id} className="flex gap-2 items-center bg-slate-50 p-2 rounded-lg border border-slate-100">
                        <span className="text-[10px] text-slate-500 font-bold whitespace-nowrap">نمایش بده اگر:</span>
                        <select {...register(`options.${optionIndex}.values_config.${valueIndex}.conditions.${k}.required_ref_id`)} className="flex-1 bg-white border border-slate-200 text-xs rounded px-2 py-1">
                            <option value="">انتخاب کنید...</option>
                            {availableDependencies.map((dep, i) => (
                                <option key={i} value={dep.ref}>{dep.optLabel} ➔ {dep.valLabel}</option>
                            ))}
                        </select>
                        <input type="hidden" {...register(`options.${optionIndex}.values_config.${valueIndex}.conditions.${k}.action`)} value="show" />
                        <button type="button" onClick={() => removeCond(k)} className="text-error/70 hover:text-error"><Trash2 size={14}/></button>
                    </div>
                ))}
                {condFields.length === 0 && <p className="text-[10px] text-slate-400">همیشه نمایش داده می‌شود (بدون شرط)</p>}
            </div>
        </div>
    );
};

// --- کامپوننت ماتریس قیمت تیراژ (محصولات خاص) ---
const QuantityPriceManager = ({ optionIndex, valueIndex }) => {
    const { control, register } = useFormContext();
    const { fields: qpFields, append: appendQp, remove: removeQp } = useFieldArray({
        control,
        name: `options.${optionIndex}.values_config.${valueIndex}.quantity_prices`
    });

    return (
        <div className="bg-white p-4 rounded-xl border border-slate-200">
            <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-extrabold text-slate-700 flex items-center gap-1.5"><Calculator size={14} className="text-purple-500"/> ماتریس قیمت تیراژ</span>
                <button type="button" onClick={() => appendQp({ quantity_id: "", price: 0 })} className="text-[10px] text-purple-600 font-bold hover:underline">+ افزودن قیمت تیراژ</button>
            </div>

            <div className="space-y-2 max-h-40 overflow-y-auto custom-scrollbar pr-1">
                {qpFields.map((qp, k) => (
                    <div key={qp.id} className="flex gap-2 items-center bg-slate-50 p-2 rounded-lg border border-slate-100">
                        <input {...register(`options.${optionIndex}.values_config.${valueIndex}.quantity_prices.${k}.quantity_id`)} placeholder="ID تیراژ" className="w-1/3 bg-white border border-slate-200 text-xs rounded px-2 py-1 text-center font-mono"/>
                        <span className="text-[10px] text-slate-400">=</span>
                        <input type="number" {...register(`options.${optionIndex}.values_config.${valueIndex}.quantity_prices.${k}.price`)} placeholder="قیمت (IQD)" className="flex-1 bg-white border border-slate-200 text-xs rounded px-2 py-1 text-left dir-ltr font-mono text-emerald-600"/>
                        <button type="button" onClick={() => removeQp(k)} className="text-error/70 hover:text-error"><Trash2 size={14}/></button>
                    </div>
                ))}
                {qpFields.length === 0 && <p className="text-[10px] text-slate-400 leading-relaxed">برای محصولات عادی خالی بگذارید.<br/>فقط برای محصولات تیراژی پر شود.</p>}
            </div>
        </div>
    );
};

export default ValuesManager;