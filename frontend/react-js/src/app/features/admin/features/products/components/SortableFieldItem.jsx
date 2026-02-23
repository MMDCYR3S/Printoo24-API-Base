import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { useFormContext, useWatch } from 'react-hook-form';
import { Trash2, GripVertical, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

import ChoicesManager from './ChoicesManager'; 
import FieldConditions from './FieldConditions';

const underlineInputClass = "w-full bg-transparent border-b-2 border-slate-200 px-2 py-3 text-slate-800 placeholder-slate-300 focus:border-primary focus:outline-none transition-all duration-300 hover:border-slate-300";

const SortableFieldItem = ({ id, index, expanded, onToggle, onRemove }) => {
    const { register, control } = useFormContext();
    
    // مقادیر برای نمایش زنده در هدر آکاردئون
    const title = useWatch({ control, name: `fields.${index}.title` });
    const fieldType = useWatch({ control, name: `fields.${index}.field_type` });
    const isRequired = useWatch({ control, name: `fields.${index}.is_required` });

    // کدهای مربوط به dnd-kit
    const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id });
    const style = { transform: CSS.Transform.toString(transform), transition, zIndex: isDragging ? 50 : 1 };

    return (
        <div ref={setNodeRef} style={style} className={clsx(
            "bg-white border rounded-[1.5rem] transition-colors duration-300 relative", 
            expanded ? "border-blue-500/30 shadow-xl shadow-blue-500/5 ring-4 ring-blue-500/5" : "border-slate-100 shadow-sm hover:border-slate-300",
            isDragging && "opacity-50 shadow-2xl"
        )}>
            {/* هدر آکاردئون */}
            <div className="flex items-center gap-4 p-5 cursor-pointer rounded-t-[1.5rem]" onClick={onToggle}>
                {/* دکمه هندلر درگ */}
                <div {...attributes} {...listeners} className="cursor-grab text-slate-300 hover:text-slate-500 p-1 touch-none">
                    <GripVertical size={20}/>
                </div>
                
                <div className="flex-1">
                    <h4 className="font-extrabold text-slate-800 text-lg">
                        {title || <span className="text-slate-400 italic">فیلد بدون نام...</span>}
                    </h4>
                    <div className="flex items-center gap-2 mt-1.5">
                        <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md text-[10px] font-bold">{fieldType}</span>
                        {isRequired && <span className="text-[10px] text-error bg-error/10 px-2 py-0.5 rounded-md font-bold">اجباری</span>}
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <button type="button" onClick={(e) => { e.stopPropagation(); onRemove(); }} className="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-error hover:bg-red-50 rounded-full transition-colors">
                        <Trash2 size={18}/>
                    </button>
                    <div className={clsx("w-8 h-8 flex items-center justify-center rounded-full bg-slate-50 text-slate-500 transition-transform duration-300", expanded && "rotate-180 bg-blue-500/10 text-blue-600")}>
                        <ChevronDown size={20}/>
                    </div>
                </div>
            </div>

            {/* بدنه آکاردئون */}
            <AnimatePresence>
                {expanded && (
                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                        <div className="border-t border-slate-100 p-6 space-y-6 bg-slate-50/30 rounded-b-[1.5rem]">
                            
                            {/* تنظیمات اصلی فیلد */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div>
                                    <label className="block text-sm font-extrabold text-slate-800 mb-2">عنوان فیلد</label>
                                    <input {...register(`fields.${index}.title`)} className={underlineInputClass} placeholder="مثال: نوع کاغذ" />
                                </div>
                                <div>
                                    <label className="block text-sm font-extrabold text-slate-800 mb-2">نوع ورودی</label>
                                    <select {...register(`fields.${index}.field_type`)} className={underlineInputClass}>
                                        <option value="dropdown">لیست کشویی (Dropdown)</option>
                                        <option value="single_select">تک انتخابی (Radio)</option>
                                    </select>
                                </div>
                            </div>

                            {/* تنظیمات اجباری بودن */}
                            <div className="flex items-center gap-3 bg-white p-4 rounded-xl border border-slate-200">
                                <label className="cursor-pointer flex items-center gap-3 shrink-0">
                                    <input type="checkbox" {...register(`fields.${index}.is_required`)} className="toggle toggle-error toggle-md"/>
                                    <span className="text-sm font-extrabold text-slate-700">پاسخ اجباری است</span>
                                </label>
                            </div>

                            {/* شروط فیلد (آیا اصلاً نمایش داده شود؟) */}
                            <FieldConditions fieldIndex={index} />

                            {/* گزینه‌های فیلد (اگر نوعش انتخابی است) */}
                            {(fieldType === 'dropdown' || fieldType === 'single_select') && (
                                <ChoicesManager fieldIndex={index} />
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default SortableFieldItem;