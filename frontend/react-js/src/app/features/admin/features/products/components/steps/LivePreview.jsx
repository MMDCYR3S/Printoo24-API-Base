import React, { useState, useMemo } from 'react';
import { useFormContext, useWatch } from 'react-hook-form';
import { Smartphone, Eye, ImageIcon, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const LivePreview = () => {
    const { control } = useFormContext();
    // مانیتور کردن کل گزینه‌ها برای رندر زنده
    const options = useWatch({ control, name: "options" }) || [];
    
    // استیت محلی برای شبیه‌سازی انتخاب‌های مشتری در پیش‌نمایش
    // آرایه‌ای از ref_id یا id های انتخاب شده
    const [mockSelections, setMockSelections] = useState([]);

    // تابع هندل کردن انتخاب‌های کاربر در محیط پیش‌نمایش
    const handleSelect = (optionIndex, valueRefId, isMultiple = false) => {
        if (!valueRefId) return;

        setMockSelections(prev => {
            if (isMultiple) {
                // برای چک‌باکس (چند انتخابی)
                return prev.includes(valueRefId) 
                    ? prev.filter(id => id !== valueRefId)
                    : [...prev, valueRefId];
            } else {
                // برای رادیو و سلکت (تک انتخابی): باید انتخاب قبلی این ویژگی رو پاک کنیم و جدید رو بذاریم
                const currentOptionValues = options[optionIndex]?.values_config.map(v => v.ref_id || v.id) || [];
                const filtered = prev.filter(id => !currentOptionValues.includes(id));
                return [...filtered, valueRefId];
            }
        });
    };

    // محاسبه قیمت تخمینی بر اساس انتخاب‌های شبیه‌سازی شده
    const estimatedTotal = useMemo(() => {
        let total = 0;
        options.forEach(opt => {
            opt.values_config?.forEach(val => {
                const valId = val.ref_id || val.id;
                if (mockSelections.includes(valId) && val.price_impact) {
                    total += Number(val.price_impact);
                }
            });
        });
        return total;
    }, [options, mockSelections]);

    // بررسی اینکه آیا یک مقدار (value) با توجه به شروطش باید نمایش داده شود یا نه؟
    const isValueVisible = (val) => {
        if (!val.conditions || val.conditions.length === 0) return true; // بدون شرط = همیشه نمایان
        // اگر شرط داشت، چک میکنیم آیا required_ref_id در انتخاب‌های فعلی (mockSelections) هست؟
        return val.conditions.some(cond => mockSelections.includes(cond.required_ref_id));
    };

    return (
        <div className="relative">
            {/* قاب فیزیکی موبایل */}
            <div className="mx-auto w-[320px] lg:w-[360px] h-[700px] bg-slate-900 border-[10px] border-slate-800 rounded-[3rem] shadow-2xl shadow-slate-900/40 relative overflow-hidden ring-1 ring-slate-700">
                
                {/* ناچ بالای موبایل */}
                <div className="absolute top-0 inset-x-0 h-6 bg-slate-800 rounded-b-2xl w-40 mx-auto z-50 flex justify-center items-center gap-2">
                    <div className="w-10 h-1.5 bg-slate-900 rounded-full"></div>
                    <div className="w-2 h-2 bg-slate-900 rounded-full"></div>
                </div>

                {/* استاتوس بار موبایل */}
                <div className="absolute top-0 inset-x-0 h-8 px-5 flex justify-between items-center z-40 text-[10px] text-slate-800 font-medium">
                    <span>9:41</span>
                    <div className="flex gap-1">
                        <div className="w-3 h-3 rounded-full bg-slate-800"></div>
                        <div className="w-3 h-3 rounded-full bg-slate-800"></div>
                    </div>
                </div>

                {/* محتوای داخل صفحه موبایل */}
                <div className="w-full h-full bg-[#f8fafc] overflow-y-auto custom-scrollbar pt-12 pb-8 relative">
                    
                    {/* هدر اپلیکیشن/سایت در موبایل */}
                    <div className="px-6 mb-4 pb-6 border-b border-slate-200/60 flex items-center gap-4">
                        <div className="w-16 h-16 bg-white shadow-sm rounded-2xl flex items-center justify-center shrink-0">
                            <ImageIcon className="text-slate-300" size={28}/>
                        </div>
                        <div>
                            <div className="h-3 w-24 bg-slate-200 rounded-full mb-2"></div>
                            <div className="h-2 w-16 bg-slate-200 rounded-full"></div>
                        </div>
                    </div>

                    {/* رندر فرم زنده */}
                    <div className="px-6 space-y-6">
                        <h4 className="font-extrabold text-slate-800 flex items-center gap-2 text-sm border-r-4 border-primary pr-2">
                            مشخصات سفارش
                        </h4>

                        {options.length === 0 ? (
                            <div className="text-center py-16 opacity-30 flex flex-col items-center">
                                <Smartphone size={48} className="mb-4 text-slate-400"/>
                                <p className="text-sm font-bold text-slate-500">مشتری اینجا فرم را می‌بیند</p>
                            </div>
                        ) : (
                            <AnimatePresence>
                                {options.map((opt, i) => {
                                    // فیلتر کردن مقادیری که شروطشون پاس نشده
                                    const visibleValues = (opt.values_config || []).filter(isValueVisible);
                                    
                                    // اگر ویژگی هیچ مقدار قابل نمایشی نداشت (مخفی شده بود)، کلاً ویژگی رو نشون نده
                                    if (visibleValues.length === 0 && ['select', 'radio', 'checkbox'].includes(opt.input_type)) return null;

                                    return (
                                        <motion.div 
                                            key={opt.id || i}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, height: 0 }}
                                            className="bg-white p-5 rounded-3xl shadow-sm border border-slate-100"
                                        >
                                            <label className="block mb-3">
                                                <span className="text-sm font-extrabold text-slate-800 flex items-center gap-1.5">
                                                    {opt.label || "ویژگی بدون نام"}
                                                    {opt.is_required && <span className="text-error text-lg leading-none">*</span>}
                                                </span>
                                                {opt.guide_text && <span className="block text-[10px] font-bold text-slate-500 mt-1">{opt.guide_text}</span>}
                                            </label>

                                            {/* رندر بر اساس نوع ورودی */}
                                            {opt.input_type === 'select' && (
                                                <div className="relative">
                                                    <select 
                                                        onChange={(e) => handleSelect(i, e.target.value)}
                                                        className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-xs font-bold rounded-xl px-3 py-3 appearance-none focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-sm"
                                                    >
                                                        <option value="">انتخاب کنید...</option>
                                                        {visibleValues.map((val, idx) => (
                                                            <option key={idx} value={val.ref_id || val.id}>
                                                                {val.label} {val.price_impact > 0 ? `(+${Number(val.price_impact).toLocaleString()})` : ''}
                                                            </option>
                                                        ))}
                                                    </select>
                                                    <ChevronDown size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"/>
                                                </div>
                                            )}

                                            {opt.input_type === 'radio' && (
                                                <div className="flex flex-col gap-2.5">
                                                    {visibleValues.map((val, idx) => {
                                                        const valId = val.ref_id || val.id;
                                                        return (
                                                            <label key={idx} className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-xl cursor-pointer hover:border-primary/50 hover:bg-slate-50 transition-colors shadow-sm">
                                                                <input 
                                                                    type="radio" 
                                                                    name={`preview_${i}`} 
                                                                    className="radio radio-xs radio-primary"
                                                                    onChange={() => handleSelect(i, valId)}
                                                                />
                                                                <span className="text-xs font-bold text-slate-700 flex-1">{val.label || "گزینه خالی"}</span>
                                                                {val.price_impact > 0 && <span className="text-[10px] font-mono text-emerald-600 font-black bg-emerald-50 px-2 py-1 rounded-md">+{Number(val.price_impact).toLocaleString()}</span>}
                                                            </label>
                                                        )
                                                    })}
                                                </div>
                                            )}

                                            {opt.input_type === 'checkbox' && (
                                                <div className="flex flex-col gap-2.5">
                                                    {visibleValues.map((val, idx) => {
                                                        const valId = val.ref_id || val.id;
                                                        return (
                                                            <label key={idx} className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-xl cursor-pointer hover:border-primary/50 hover:bg-slate-50 transition-colors shadow-sm">
                                                                <input 
                                                                    type="checkbox" 
                                                                    className="checkbox checkbox-xs checkbox-primary rounded-md"
                                                                    onChange={() => handleSelect(i, valId, true)}
                                                                />
                                                                <span className="text-xs font-bold text-slate-700 flex-1">{val.label || "گزینه خالی"}</span>
                                                                {val.price_impact > 0 && <span className="text-[10px] font-mono text-emerald-600 font-black bg-emerald-50 px-2 py-1 rounded-md">+{Number(val.price_impact).toLocaleString()}</span>}
                                                            </label>
                                                        )
                                                    })}
                                                </div>
                                            )}

                                            {(opt.input_type === 'text' || opt.input_type === 'textarea') && (
                                                <input disabled className="w-full bg-slate-50 border border-slate-200 text-slate-400 text-xs font-bold rounded-xl px-3 py-3" placeholder="محل تایپ مشتری..."/>
                                            )}
                                        </motion.div>
                                    );
                                })}
                            </AnimatePresence>
                        )}
                        
                        {/* نمایش مجموع قیمت شبیه‌سازی شده */}
                        {options.length > 0 && (
                            <div className="mt-8 pt-6 border-t border-slate-200/60">
                                <div className="flex justify-between items-center bg-emerald-50 text-emerald-700 p-4 rounded-2xl border border-emerald-100">
                                    <span className="text-xs font-extrabold">مبلغ آپشن‌ها (تخمینی)</span>
                                    <span className="font-mono text-lg font-black tracking-tight">+{estimatedTotal.toLocaleString()} IQD</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* دکمه Home پایین آیفون */}
                <div className="absolute bottom-2 inset-x-0 flex justify-center z-50 pointer-events-none">
                    <div className="w-24 h-1 bg-slate-300/50 rounded-full"></div>
                </div>
            </div>

            {/* نشانگر وضعیت پیش‌نمایش */}
            <div className="text-center mt-6 text-sm font-bold text-slate-400 flex items-center justify-center gap-2 bg-white/50 py-2 rounded-full w-max mx-auto px-6 shadow-sm border border-white">
                <Eye size={18} className="text-primary"/> پیش‌نمایش زنده و هوشمند
            </div>
        </div>
    );
};

export default LivePreview;