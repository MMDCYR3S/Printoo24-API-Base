import React, { useEffect, useMemo } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import { Save, Layers, DollarSign, Package, AlertCircle, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
// مسیر ایمپورت سرویس دسته‌بندی
import { adminCategoryService } from '../../../../services/adminCategoryService'; 

const underlineInputClass = "w-full bg-transparent border-b-2 border-slate-200 px-2 py-3 text-slate-800 placeholder-slate-300 focus:border-blue-500 focus:outline-none transition-all duration-300 hover:border-slate-300";

const ProductStep1Form = ({ initialData, onSave, isSaving, isEditMode }) => {
    
    const { data: categories = [], isLoading: isCategoriesLoading } = useQuery({
        queryKey: ['admin-all-categories-dropdown'],
        queryFn: () => adminCategoryService.getRoots(),
        staleTime: 1000 * 60 * 5, 
    });

    const { register, handleSubmit, control, reset, setValue } = useForm({
        defaultValues: {
            shell: {
                name: "",
                category_id: "",
                subcategory_id: "",
                description: "",
                has_price: true,
                show_price: "",
                price_per_unit: "",
                has_quantity: false,
                min_quantity: "1",
                max_quantity: "",
                is_active: true,
                guide_text: "",
                guide_type: "info"
            }
        }
    });

    const hasPrice = useWatch({ control, name: 'shell.has_price' });
    const hasQuantity = useWatch({ control, name: 'shell.has_quantity' });
    const selectedCategoryId = useWatch({ control, name: 'shell.category_id' });

    // لیست فرزندان بر اساس دسته اصلی انتخاب شده
    const availableSubcategories = useMemo(() => {
        if (!selectedCategoryId || !categories?.length) return [];
        const parent = categories.find(c => c.id.toString() === selectedCategoryId.toString());
        return parent?.children || [];
    }, [selectedCategoryId, categories]);

    // پر کردن فرم در حالت ویرایش
    useEffect(() => {
        if (initialData?.shell && categories?.length > 0) {
            const s = initialData.shell;
            
            let pId = s.category_id || "";
            let cId = s.subcategory_id || "";

            // در صورتی که بک‌اند هنوز فرمت قدیمی رو تو GET برمی‌گردوند (محض اطمینان)
            if (!pId && s.category_info?.id) {
                const targetId = s.category_info.id;
                for (const parent of categories) {
                    if (parent.id.toString() === targetId.toString()) {
                        pId = parent.id.toString();
                        break;
                    }
                    const foundChild = parent.children?.find(c => c.id.toString() === targetId.toString());
                    if (foundChild) {
                        pId = parent.id.toString();
                        cId = foundChild.id.toString();
                        break;
                    }
                }
            }

            reset({
                shell: {
                    name: s.name || "",
                    category_id: pId,
                    subcategory_id: cId,
                    description: s.description || "",
                    has_price: s.has_price !== undefined ? Boolean(s.has_price) : true,
                    show_price: s.show_price || "",
                    price_per_unit: s.price_per_unit || "",
                    has_quantity: s.has_quantity !== undefined ? Boolean(s.has_quantity) : false,
                    min_quantity: s.min_quantity || "1",
                    max_quantity: s.max_quantity || "",
                    is_active: s.is_active !== undefined ? Boolean(s.is_active) : true,
                    guide_text: s.guide_text || "",
                    guide_type: s.guide_type || "info"
                }
            });
        }
    }, [initialData, categories, reset]);

    // وقتی تو حالت ایجاد محصول هستیم و دسته پدر عوض میشه، زیردسته رو ریست کن
    useEffect(() => {
        if (!isEditMode) {
            setValue('shell.subcategory_id', '');
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedCategoryId, isEditMode]);

    const onSubmit = (data) => {
        onSave(data);
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8 pb-32">
            
            {/* 1. اطلاعات پایه */}
            <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 rounded-[2rem]">
                <div className="flex items-center gap-4 mb-8 pb-4 border-b border-slate-100">
                    <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                        <Layers size={24} />
                    </div>
                    <div>
                        <h3 className="text-xl font-black text-slate-800">مشخصات اصلی</h3>
                        <p className="text-sm text-slate-500 font-medium mt-1">نام، دسته‌بندی و وضعیت نمایش محصول</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="md:col-span-2">
                        <label className="block text-sm font-extrabold text-slate-800 mb-2">نام محصول <span className="text-error">*</span></label>
                        <input 
                            {...register('shell.name', { required: true })} 
                            className={underlineInputClass} 
                            placeholder="مثال: کارت ویزیت لمینت براق" 
                        />
                    </div>
                    
                    {/* دراپ داون اول: دسته اصلی */}
                    <div className="relative">
                        <label className="block text-sm font-extrabold text-slate-800 mb-2">دسته‌بندی اصلی <span className="text-error">*</span></label>
                        <select 
                            {...register('shell.category_id', { required: true })} 
                            className={clsx(underlineInputClass, "cursor-pointer font-bold text-sm", isCategoriesLoading && "opacity-50")}
                            disabled={isCategoriesLoading}
                        >
                            <option value="">{isCategoriesLoading ? "در حال بارگذاری..." : "انتخاب دسته اصلی..."}</option>
                            {categories.map(cat => (
                                <option key={cat.id} value={cat.id}>{cat.name}</option>
                            ))}
                        </select>
                        {isCategoriesLoading && <Loader2 className="absolute left-2 top-10 animate-spin text-blue-500" size={16} />}
                    </div>

                    {/* دراپ داون دوم: زیر دسته */}
                    <div>
                        <label className="block text-sm font-extrabold text-slate-800 mb-2">زیردسته <span className="text-error">*</span></label>
                        <select 
                            {...register('shell.subcategory_id', { required: true })} 
                            className={clsx(underlineInputClass, "cursor-pointer font-bold text-sm")}
                            disabled={!selectedCategoryId || availableSubcategories.length === 0}
                        >
                            <option value="">انتخاب زیردسته...</option>
                            {availableSubcategories.map(child => (
                                <option key={child.id} value={child.id}>{child.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="md:col-span-2">
                        <label className="block text-sm font-extrabold text-slate-800 mb-2">توضیحات کوتاه</label>
                        <textarea 
                            {...register('shell.description')} 
                            className={clsx(underlineInputClass, "resize-none h-24")} 
                            placeholder="ویژگی‌ها و توضیحات کلی محصول..."
                        ></textarea>
                    </div>

                    <div className="md:col-span-2 flex items-center gap-4 bg-slate-50 p-4 rounded-2xl border border-slate-100">
                        <label className="cursor-pointer flex items-center gap-3">
                            <input type="checkbox" {...register('shell.is_active')} className="toggle toggle-success"/>
                            <span className="font-extrabold text-slate-700">محصول در فروشگاه فعال باشد (قابل سفارش)</span>
                        </label>
                    </div>
                </div>
            </div>

            {/* 2. تنظیمات قیمت */}
            <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 rounded-[2rem]">
                <div className="flex justify-between items-center mb-8 pb-4 border-b border-slate-100">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                            <DollarSign size={24} />
                        </div>
                        <div>
                            <h3 className="text-xl font-black text-slate-800">قیمت‌گذاری</h3>
                            <p className="text-sm text-slate-500 font-medium mt-1">تنظیمات پایه قیمت محصول</p>
                        </div>
                    </div>
                    <label className="cursor-pointer flex items-center gap-3 bg-white border border-slate-200 px-4 py-2 rounded-full shadow-sm">
                        <input type="checkbox" {...register('shell.has_price')} className="toggle toggle-primary toggle-sm"/>
                        <span className="text-sm font-bold text-slate-700">این محصول قیمت دارد</span>
                    </label>
                </div>

                <AnimatePresence>
                    {hasPrice ? (
                        <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                                <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100 relative">
                                    <label className="block text-xs font-black text-slate-600 mb-3">قیمت نمایشی (خط خورده)</label>
                                    <input type="number" {...register('shell.show_price')} className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-left dir-ltr font-mono font-bold text-slate-400 focus:border-blue-500 outline-none" placeholder="0" />
                                    <span className="absolute left-8 top-[46px] text-[10px] text-slate-400 font-bold">IQD</span>
                                </div>
                                <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100 relative">
                                    <label className="block text-xs font-black text-slate-600 mb-3">قیمت هر واحد (Price Per Unit)</label>
                                    <input type="number" step="any" {...register('shell.price_per_unit')} className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-left dir-ltr font-mono font-bold text-purple-600 focus:border-purple-500 outline-none" placeholder="0" />
                                    <span className="absolute left-8 top-[46px] text-[10px] text-slate-400 font-bold">IQD</span>
                                </div>
                            </div>
                        </motion.div>
                    ) : (
                        <div className="text-center py-8 text-amber-600 bg-amber-50 rounded-2xl border border-amber-100 font-bold text-sm">
                            این محصول بدون قیمت (استعلامی / توافقی) ثبت خواهد شد.
                        </div>
                    )}
                </AnimatePresence>
            </div>

            {/* 3. استراتژی فروش */}
            <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 rounded-[2rem]">
                <div className="flex justify-between items-center mb-8 pb-4 border-b border-slate-100">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                            <Package size={24} />
                        </div>
                        <div>
                            <h3 className="text-xl font-black text-slate-800">استراتژی فروش</h3>
                            <p className="text-sm text-slate-500 font-medium mt-1">آیا کاربر باید تعداد دلخواه وارد کند؟</p>
                        </div>
                    </div>
                    <label className="cursor-pointer flex items-center gap-3 bg-white border border-slate-200 px-4 py-2 rounded-full shadow-sm">
                        <input type="checkbox" {...register('shell.has_quantity')} className="toggle toggle-primary toggle-sm"/>
                        <span className="text-sm font-bold text-slate-700">محصول تعدادی است (ورودی دلخواه)</span>
                    </label>
                </div>

                <AnimatePresence>
                    {hasQuantity ? (
                        <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                                <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                                    <label className="block text-xs font-black text-slate-600 mb-3">حداقل تعداد مجاز سفارش</label>
                                    <input type="number" {...register('shell.min_quantity')} className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-center dir-ltr font-mono font-bold focus:border-blue-500 outline-none" placeholder="1" />
                                </div>
                                <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                                    <label className="block text-xs font-black text-slate-600 mb-3">حداکثر تعداد مجاز (خالی = نامحدود)</label>
                                    <input type="number" {...register('shell.max_quantity')} className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-center dir-ltr font-mono font-bold focus:border-blue-500 outline-none" placeholder="نامحدود" />
                                </div>
                            </div>
                        </motion.div>
                    ) : (
                        <div className="text-center py-6 text-slate-500 bg-slate-50 rounded-2xl border border-slate-100 font-bold text-sm">
                            این محصول بر اساس ویژگی‌ها (مثل منوی کشویی تیراژ) فروخته می‌شود و باکس تعداد سفارشی ندارد.
                        </div>
                    )}
                </AnimatePresence>
            </div>

            {/* 4. راهنمای کاربر */}
            <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 rounded-[2rem]">
                <div className="flex items-center gap-4 mb-8 pb-4 border-b border-slate-100">
                    <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
                        <AlertCircle size={24} />
                    </div>
                    <div>
                        <h3 className="text-xl font-black text-slate-800">پیام راهنما</h3>
                        <p className="text-sm text-slate-500 font-medium mt-1">پیامی که در صفحه محصول به مشتری نمایش داده می‌شود</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                    <div className="md:col-span-4">
                        <label className="block text-sm font-extrabold text-slate-800 mb-2">نوع پیام</label>
                        <select {...register('shell.guide_type')} className={clsx(underlineInputClass, "font-bold text-sm cursor-pointer")}>
                            <option value="info">اطلاعات (آبی)</option>
                            <option value="warning">هشدار (زرد/نارنجی)</option>
                            <option value="tip">نکته آموزشی (سبز)</option>
                        </select>
                    </div>
                    <div className="md:col-span-8">
                        <label className="block text-sm font-extrabold text-slate-800 mb-2">متن پیام</label>
                        <input 
                            {...register('shell.guide_text')} 
                            className={underlineInputClass} 
                            placeholder="مثال: زمان تحویل این محصول ۷ روز کاری است..." 
                        />
                    </div>
                </div>
            </div>

            {/* دکمه شناور ذخیره */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex justify-center w-full px-6 pointer-events-none">
                <div className="bg-white/80 backdrop-blur-md p-3 rounded-full shadow-[0_20px_50px_-12px_rgba(0,0,0,0.15)] border border-white/50 pointer-events-auto">
                    <button 
                        type="submit" 
                        disabled={isSaving} 
                        className="btn bg-blue-600 hover:bg-blue-700 text-white h-14 px-12 rounded-full shadow-lg shadow-blue-500/40 text-lg font-black hover:scale-[1.02] active:scale-95 transition-all gap-3 border-none flex items-center"
                    >
                        {isSaving ? <span className="loading loading-spinner"></span> : <Save size={24}/>}
                        {isEditMode ? 'ذخیره تغییرات و ادامه' : 'ایجاد هسته محصول و ادامه'}
                    </button>
                </div>
            </div>
        </form>
    );
};

export default ProductStep1Form;