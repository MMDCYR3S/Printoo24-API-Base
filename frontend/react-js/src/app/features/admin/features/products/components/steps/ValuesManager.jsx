import React, { useState, useEffect } from 'react';
import { useFormContext, useFieldArray, useWatch } from 'react-hook-form';
import { Plus, Trash2, GripVertical, Settings2, ListPlus, Link2, Calculator } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import { generateRefId, useStep2Data } from '../../../../hooks/useStep2Form';

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
            ref_id: generateRefId('val'), // الزامی طبق داکیومنت برای شروط
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

// --- کامپوننت سطر هر مقدار ---
const ValueRow = ({ optionIndex, valueIndex, remove }) => {
    const [showAdvanced, setShowAdvanced] = useState(false);
    const { register, control } = useFormContext();
    
    const price = useWatch({ control, name: `options.${optionIndex}.values_config.${valueIndex}.price_impact` });
    
    return (
        <div className="flex flex-col bg-slate-50/80 rounded-2xl border border-slate-100 shadow-sm group hover:bg-white hover:border-slate-200 transition-all relative">
            
            <input type="hidden" {...register(`options.${optionIndex}.values_config.${valueIndex}.id`)} />
            <input type="hidden" {...register(`options.${optionIndex}.values_config.${valueIndex}.ref_id`)} />

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

            <AnimatePresence>
                {showAdvanced && (
                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                        <div className="p-5 border-t border-slate-200 bg-slate-100/50 rounded-b-2xl grid grid-cols-1 xl:grid-cols-2 gap-6">
                            <ConditionManager optionIndex={optionIndex} valueIndex={valueIndex} />
                            <QuantityPriceManager optionIndex={optionIndex} valueIndex={valueIndex} />
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

// --- کامپوننت شروط ---
const ConditionManager = ({ optionIndex, valueIndex }) => {
    const { control, register } = useFormContext();
    const allOptions = useWatch({ control, name: 'options' }) || [];
    
    const { fields: condFields, append: appendCond, remove: removeCond } = useFieldArray({
        control,
        name: `options.${optionIndex}.values_config.${valueIndex}.conditions`
    });

    const availableDependencies = allOptions.reduce((acc, opt, idx) => {
        if (idx === optionIndex) return acc;
        const values = opt.values_config || [];
        values.forEach(val => {
            if (val.label && val.ref_id) {
                acc.push({ optLabel: opt.label, valLabel: val.label, ref: val.ref_id });
            }
        });
        return acc;
    }, []);

    return (
        <div className="bg-white p-4 rounded-xl border border-slate-200 h-full">
            <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-extrabold text-slate-700 flex items-center gap-1.5"><Link2 size={14} className="text-primary"/> شروط نمایش (وابستگی)</span>
                <button type="button" onClick={() => appendCond({ required_ref_id: "", action: "show" })} className="text-[10px] text-primary font-bold hover:underline">+ افزودن شرط</button>
            </div>
            
            <div className="space-y-2 overflow-y-auto custom-scrollbar max-h-40 pr-1">
                {condFields.map((cond, k) => (
                    <div key={cond.id} className="flex gap-2 items-center bg-slate-50 p-2 rounded-lg border border-slate-100">
                        <span className="text-[10px] text-slate-500 font-bold whitespace-nowrap">نمایش بده اگر:</span>
                        <select {...register(`options.${optionIndex}.values_config.${valueIndex}.conditions.${k}.required_ref_id`)} className="flex-1 bg-white border border-slate-200 text-xs rounded px-2 py-1.5 focus:border-primary outline-none">
                            <option value="">انتخاب کنید...</option>
                            {availableDependencies.map((dep, i) => (
                                <option key={i} value={dep.ref}>{dep.optLabel} ➔ {dep.valLabel}</option>
                            ))}
                        </select>
                        <input type="hidden" {...register(`options.${optionIndex}.values_config.${valueIndex}.conditions.${k}.action`)} value="show" />
                        <button type="button" onClick={() => removeCond(k)} className="text-error/70 hover:text-error p-1"><Trash2 size={14}/></button>
                    </div>
                ))}
                {condFields.length === 0 && (
                    <div className="text-center py-4">
                        <p className="text-[10px] text-slate-400">همیشه نمایش داده می‌شود (بدون شرط)</p>
                    </div>
                )}
            </div>
        </div>
    );
};

// --- کامپوننت ماتریس تیراژ ---
const QuantityPriceManager = ({ optionIndex, valueIndex }) => {
    const { control, register } = useFormContext();
    const { productQuantities, isLoadingQuantities } = useStep2Data(); 

    const { fields: qpFields, replace } = useFieldArray({
        control,
        name: `options.${optionIndex}.values_config.${valueIndex}.quantity_prices`
    });

    useEffect(() => {
        if (productQuantities && productQuantities.length > 0) {
            if (qpFields.length === 0) {
                const defaultPrices = productQuantities.map(q => ({
                    quantity_id: q.quantity_id,
                    price: 0
                }));
                replace(defaultPrices);
            }
        }
    }, [productQuantities, qpFields.length, replace]);

    if (isLoadingQuantities) {
        return (
            <div className="bg-slate-50 p-6 rounded-xl border border-slate-200 text-center flex flex-col items-center justify-center h-full">
                <span className="loading loading-spinner loading-md text-purple-400 mb-2"></span>
                <span className="text-xs font-bold text-slate-400">در حال دریافت تیراژهای محصول...</span>
            </div>
        );
    }

    if (!productQuantities || productQuantities.length === 0) {
        return (
            <div className="bg-slate-50 p-6 rounded-xl border border-slate-200 text-center flex items-center justify-center h-full">
                <span className="text-xs font-bold text-slate-400 leading-relaxed">این محصول دارای تیراژ ثابت نیست.<br/>(ماتریس قیمت غیرفعال)</span>
            </div>
        );
    }

    return (
        <div className="bg-white p-4 rounded-xl border border-slate-200 h-full flex flex-col">
            <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-extrabold text-slate-700 flex items-center gap-1.5"><Calculator size={14} className="text-purple-500"/> ماتریس قیمت افزوده بر اساس تیراژ</span>
            </div>

            <div className="space-y-2 overflow-y-auto custom-scrollbar pr-1 max-h-40 flex-1">
                {qpFields.map((qp, k) => {
                    const qData = productQuantities.find(q => q.quantity_id === qp.quantity_id);
                    const displayValue = qData ? qData.value : qp.quantity_id;

                    return (
                        <div key={qp.id} className="flex gap-2 items-center bg-slate-50 p-2 rounded-lg border border-slate-100 transition-colors hover:border-purple-200">
                            <div className="w-1/3 bg-slate-200/50 border border-slate-200 text-xs rounded px-2 py-1.5 text-center font-extrabold text-slate-600">
                                تیراژ: {displayValue}
                            </div>
                            <input type="hidden" {...register(`options.${optionIndex}.values_config.${valueIndex}.quantity_prices.${k}.quantity_id`)} />
                            <span className="text-[10px] text-slate-400 font-bold">=</span>
                            <div className="flex-1 relative group">
                                <input 
                                    type="number" 
                                    {...register(`options.${optionIndex}.values_config.${valueIndex}.quantity_prices.${k}.price`)} 
                                    placeholder="0" 
                                    className="w-full bg-white border border-slate-200 text-xs rounded px-2 py-1.5 pl-8 text-left dir-ltr font-mono text-emerald-600 font-black focus:border-purple-400 focus:ring-1 focus:ring-purple-400 focus:shadow-sm transition-all outline-none"
                                />
                                <span className="absolute left-2 top-1/2 -translate-y-1/2 text-[9px] font-black text-slate-400 group-focus-within:text-purple-500 transition-colors">IQD</span>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    );
};

export default ValuesManager;