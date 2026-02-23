import React, { useEffect, useState } from 'react';
import { useForm, useFieldArray, FormProvider } from 'react-hook-form';
import { Save, Calculator, Plus, Trash2, Info, Variable } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const underlineInputClass = "w-full bg-transparent border-b-2 border-slate-200 px-2 py-3 text-slate-800 placeholder-slate-300 focus:border-purple-500 focus:outline-none transition-all duration-300 hover:border-slate-300 font-mono text-left dir-ltr";

const ProductStep3Formulas = ({ initialData, onSave, isSaving }) => {
    // استخراج فیلدهای دارای ID واقعی برای نمایش به عنوان متغیر
    const availableVariables = (initialData?.fields || []).filter(f => f.id).map(f => ({
        id: f.id,
        tag: `field_${f.id}`,
        title: f.title
    }));

    const methods = useForm({
        defaultValues: {
            formulas: initialData?.formulas?.length ? initialData.formulas : []
        }
    });

    const { control, handleSubmit, register } = methods;
    const { fields, append, remove } = useFieldArray({
        control,
        name: "formulas"
    });

    const onSubmit = (data) => {
        // پاکسازی و آماده‌سازی دقیقاً طبق سواگر
        const payload = {
            formulas: data.formulas.map(f => {
                const formula = {
                    title: f.title,
                    calculation_expression: f.calculation_expression,
                    condition_expression: f.condition_expression || null
                };
                if (f.id) formula.id = f.id;
                return formula;
            })
        };
        console.log("🚀 Payload استپ ۳ (فرمول‌ها):", JSON.stringify(payload, null, 2));
        onSave(payload);
    };

    const handleAddFormula = () => {
        append({
            id: null,
            title: "",
            condition_expression: "",
            calculation_expression: ""
        });
    };

    // تابع کمکی برای کپی کردن متغیر در کلیپ‌بورد تا ادمین راحت پیست کند
    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        // اینجا می‌تونی یک توست (Toast) کوچیک نشون بدی: "متغیر کپی شد"
    };

    return (
        <FormProvider {...methods}>
            <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 xl:grid-cols-12 gap-8 pb-32 relative">
                
                {/* ستون راست: فرمول‌ساز */}
                <div className="xl:col-span-8 flex flex-col gap-6">
                    <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 rounded-[2rem]">
                        <div className="flex justify-between items-start mb-8">
                            <div className="flex items-start gap-5">
                                <div className="w-14 h-14 rounded-[1.25rem] bg-gradient-to-br from-purple-500/10 to-purple-500/5 flex items-center justify-center text-purple-600 shadow-sm border border-purple-500/10">
                                    <Calculator size={26} strokeWidth={1.5} />
                                </div>
                                <div>
                                    <h3 className="font-extrabold text-slate-800 text-2xl tracking-tight">مغز محاسباتی محصول</h3>
                                    <p className="text-sm text-slate-500 mt-2 font-medium">فرمول‌های ریاضی برای محاسبه قیمت نهایی را اینجا وارد کنید.</p>
                                </div>
                            </div>
                            <button onClick={handleAddFormula} type="button" className="btn bg-purple-600 hover:bg-purple-700 text-white btn-sm rounded-full shadow-lg shadow-purple-500/30 px-6 border-none">
                                <Plus size={16}/> افزودن فرمول
                            </button>
                        </div>

                        <div className="space-y-6">
                            <AnimatePresence>
                                {fields.map((field, index) => (
                                    <motion.div 
                                        key={field.id}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, scale: 0.95 }}
                                        className="bg-white border border-slate-200 rounded-[1.5rem] p-6 shadow-sm relative group hover:border-purple-300 transition-colors"
                                    >
                                        <button 
                                            type="button" 
                                            onClick={() => remove(index)} 
                                            className="absolute top-4 left-4 w-8 h-8 flex items-center justify-center bg-red-50 text-error rounded-full opacity-0 group-hover:opacity-100 transition-all hover:bg-red-100"
                                        >
                                            <Trash2 size={16}/>
                                        </button>

                                        <input type="hidden" {...register(`formulas.${index}.id`)} />

                                        <div className="grid grid-cols-1 gap-6">
                                            {/* عنوان فرمول */}
                                            <div>
                                                <label className="block text-sm font-extrabold text-slate-800 mb-2">عنوان فرمول</label>
                                                <input 
                                                    {...register(`formulas.${index}.title`)} 
                                                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-800 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 focus:outline-none transition-all text-sm font-bold" 
                                                    placeholder="مثلاً: فرمول قیمت عمده فروشی (تیراژ بالا)" 
                                                />
                                            </div>

                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                {/* شرط فرمول */}
                                                <div className="bg-blue-50/50 p-4 rounded-xl border border-blue-100">
                                                    <label className="block text-xs font-extrabold text-blue-800 mb-2">شرط اجرا (اختیاری)</label>
                                                    <input 
                                                        {...register(`formulas.${index}.condition_expression`)} 
                                                        className={underlineInputClass} 
                                                        placeholder="e.g. field_15 >= 1000" 
                                                    />
                                                    <p className="text-[10px] text-blue-600/70 mt-2 font-medium">اگر خالی باشد، همیشه اجرا می‌شود.</p>
                                                </div>

                                                {/* محاسبه فرمول */}
                                                <div className="bg-emerald-50/50 p-4 rounded-xl border border-emerald-100">
                                                    <label className="block text-xs font-extrabold text-emerald-800 mb-2">فرمول ریاضی (الزامی)</label>
                                                    <input 
                                                        {...register(`formulas.${index}.calculation_expression`, { required: true })} 
                                                        className={clsx(underlineInputClass, "border-emerald-200 focus:border-emerald-500 font-black text-emerald-700")} 
                                                        placeholder="e.g. (field_10 * field_12) * 1.5" 
                                                    />
                                                    <p className="text-[10px] text-emerald-600/70 mt-2 font-medium">از عملگرهای + - * / ( ) استفاده کنید.</p>
                                                </div>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </AnimatePresence>

                            {fields.length === 0 && (
                                <div className="text-center py-12 bg-slate-50 border-2 border-dashed border-slate-200 rounded-[2rem]">
                                    <Calculator size={40} className="mx-auto text-slate-300 mb-3"/>
                                    <p className="text-slate-500 font-bold">هنوز هیچ فرمولی ثبت نکرده‌اید.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* ستون چپ: راهنمای متغیرها */}
                <div className="xl:col-span-4 relative">
                    <div className="sticky top-32 pt-2 space-y-4">
                        <div className="bg-white/80 backdrop-blur-xl shadow-lg shadow-slate-200/40 border border-slate-200 p-6 rounded-[2rem]">
                            <div className="flex items-center gap-3 mb-4 border-b border-slate-100 pb-4">
                                <Variable className="text-purple-500" size={20}/>
                                <h4 className="font-extrabold text-slate-800">متغیرهای در دسترس</h4>
                            </div>
                            
                            <p className="text-xs text-slate-500 font-medium leading-relaxed mb-4">
                                روی هر متغیر کلیک کنید تا کپی شود، سپس آن را در کادر فرمول (سمت راست) پیست کنید.
                            </p>

                            <div className="space-y-2 max-h-[400px] overflow-y-auto custom-scrollbar pr-1">
                                {availableVariables.map((v) => (
                                    <div 
                                        key={v.id} 
                                        onClick={() => copyToClipboard(v.tag)}
                                        className="flex items-center justify-between p-3 bg-slate-50 hover:bg-purple-50 border border-slate-100 hover:border-purple-200 rounded-xl cursor-pointer transition-colors group"
                                    >
                                        <span className="text-xs font-bold text-slate-700 group-hover:text-purple-700">{v.title}</span>
                                        <span className="text-[11px] font-mono bg-white border border-slate-200 group-hover:border-purple-300 px-2 py-1 rounded-md text-slate-500 group-hover:text-purple-600">
                                            {v.tag}
                                        </span>
                                    </div>
                                ))}

                                {availableVariables.length === 0 && (
                                    <div className="text-center p-4 bg-amber-50 rounded-xl border border-amber-100">
                                        <Info size={20} className="mx-auto text-amber-500 mb-2"/>
                                        <p className="text-[10px] font-bold text-amber-700">هیچ فیلدی در مرحله قبل ساخته نشده یا محصول هنوز ذخیره نشده است.</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* دکمه شناور ذخیره */}
                <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex justify-center w-full px-6 pointer-events-none">
                    <div className="bg-white/80 backdrop-blur-md p-3 rounded-full shadow-[0_20px_50px_-12px_rgba(0,0,0,0.15)] border border-white/50 pointer-events-auto">
                        <button type="submit" disabled={isSaving} className="btn bg-purple-600 hover:bg-purple-700 text-white h-14 px-12 rounded-full shadow-lg shadow-purple-500/40 text-lg font-black hover:scale-[1.02] active:scale-95 transition-all gap-3 border-none flex items-center">
                            {isSaving ? <span className="loading loading-spinner"></span> : <Save size={24}/>}
                            ذخیره فرمول‌ها و ادامه
                        </button>
                    </div>
                </div>
            </form>
        </FormProvider>
    );
};

export default ProductStep3Formulas;