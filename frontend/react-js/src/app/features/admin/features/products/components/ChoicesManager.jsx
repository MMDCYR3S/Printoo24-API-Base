import React from 'react';
import { useFormContext, useFieldArray } from 'react-hook-form';
import { Plus, Trash2, ArrowUp, ArrowDown } from 'lucide-react';
import { generateTempId } from '../../../hooks/useStep2Form';
import clsx from 'clsx';

const underlineInputClass = "w-full bg-transparent border-b-2 border-slate-200 px-2 py-2 text-slate-800 focus:border-primary focus:outline-none transition-all duration-300";

const ChoicesManager = ({ fieldIndex }) => {
    const { control, register } = useFormContext();
    const { fields: choices, append, remove, move } = useFieldArray({
        control,
        name: `fields.${fieldIndex}.choices`
    });

    const handleAddChoice = () => {
        append({
            id: null,
            temp_id: generateTempId('choice'),
            title: "",
            numeric_value: "0"
        });
    };

    return (
        <div className="bg-slate-50/50 rounded-2xl p-5 border border-slate-100 mt-4">
            <div className="flex justify-between items-center mb-4">
                <h5 className="font-bold text-slate-700 text-sm">گزینه‌های قابل انتخاب</h5>
                <button type="button" onClick={handleAddChoice} className="btn btn-xs btn-primary btn-outline rounded-full">
                    <Plus size={14}/> افزودن گزینه
                </button>
            </div>

            <div className="space-y-3">
                {choices.map((choice, choiceIndex) => (
                    <div key={choice.id} className="flex items-center gap-3 bg-white p-3 rounded-xl border border-slate-200 shadow-sm group">
                        
                        {/* فیلدهای مخفی برای شناسه‌ها */}
                        <input type="hidden" {...register(`fields.${fieldIndex}.choices.${choiceIndex}.id`)} />
                        <input type="hidden" {...register(`fields.${fieldIndex}.choices.${choiceIndex}.temp_id`)} />

                        {/* دکمه‌های مرتب‌سازی ساده (فعلاً جایگزین DND برای پایداری تا نصب لایبرری) */}
                        <div className="flex flex-col gap-1">
                            <button type="button" onClick={() => move(choiceIndex, choiceIndex - 1)} disabled={choiceIndex === 0} className="text-slate-300 hover:text-primary disabled:opacity-30"><ArrowUp size={14}/></button>
                            <button type="button" onClick={() => move(choiceIndex, choiceIndex + 1)} disabled={choiceIndex === choices.length - 1} className="text-slate-300 hover:text-primary disabled:opacity-30"><ArrowDown size={14}/></button>
                        </div>

                        <div className="flex-1">
                            <input 
                                {...register(`fields.${fieldIndex}.choices.${choiceIndex}.title`)}
                                className={clsx(underlineInputClass, "text-sm font-bold")}
                                placeholder="عنوان (مثلاً: گلاسه ۱۳۵)"
                            />
                        </div>

                        <div className="w-32 relative">
                            <input 
                                type="number" 
                                step="any"
                                {...register(`fields.${fieldIndex}.choices.${choiceIndex}.numeric_value`)}
                                className={clsx(underlineInputClass, "font-mono text-sm pl-8 text-left dir-ltr")}
                                placeholder="0"
                            />
                            <span className="absolute left-1 top-3 text-[10px] font-bold text-slate-400">IQD</span>
                        </div>

                        <button type="button" onClick={() => remove(choiceIndex)} className="text-error/50 hover:text-error p-2 transition-colors">
                            <Trash2 size={16}/>
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ChoicesManager;