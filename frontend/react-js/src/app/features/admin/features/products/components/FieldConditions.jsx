import React from 'react';
import { useFormContext, useFieldArray, useWatch } from 'react-hook-form';
import { Plus, Trash2, Link2 } from 'lucide-react';

const FieldConditions = ({ fieldIndex }) => {
    // 🎯 باگ اصلی اینجا بود: setValue ایمپورت نشده بود!
    const { control, register, setValue } = useFormContext(); 
    const allFields = useWatch({ control, name: 'fields' }) || [];
    
    const { fields: condFields, append, remove } = useFieldArray({
        control,
        name: `fields.${fieldIndex}.conditions`
    });

    const availableTriggers = allFields.slice(0, fieldIndex).reduce((acc, field) => {
        const fieldIdentifier = field.id || field.temp_id;
        const choices = field.choices || [];
        
        choices.forEach(choice => {
            const choiceIdentifier = choice.id || choice.temp_id;
            if (field.title && choice.title && fieldIdentifier && choiceIdentifier) {
                acc.push({
                    fieldId: fieldIdentifier,
                    choiceId: choiceIdentifier,
                    label: `${field.title} ➔ ${choice.title}`
                });
            }
        });
        return acc;
    }, []);

    if (availableTriggers.length === 0) return null; 

    return (
        <div className="bg-blue-50/50 p-4 rounded-xl border border-blue-100 mt-4">
            <div className="flex justify-between items-center mb-3">
                <span className="text-xs font-extrabold text-blue-800 flex items-center gap-1.5"><Link2 size={14}/> شروط (وابستگی این فیلد به فیلدهای قبلی)</span>
                <button type="button" onClick={() => append({ trigger_field_id: "", trigger_choice_id: "", operator: "equals", action: "show" })} className="text-[10px] text-blue-600 font-bold hover:underline">
                    + افزودن شرط جدید
                </button>
            </div>
            
            <div className="space-y-3">
                {condFields.map((cond, k) => (
                    <div key={cond.id} className="flex flex-wrap gap-2 items-center bg-white p-3 rounded-lg border border-blue-100 shadow-sm">
                        
                        <select 
                            {...register(`fields.${fieldIndex}.conditions.${k}.action`)}
                            className="bg-slate-50 border border-slate-200 text-xs py-1.5 px-2 rounded-md font-bold text-slate-700 outline-none"
                        >
                            <option value="show">آشکار شود</option>
                            <option value="hide">پنهان شود</option>
                            <option value="enable">فعال شود</option>
                            <option value="disable">غیرفعال شود</option>
                        </select>

                        <span className="text-xs text-slate-500 font-medium">اگر فیلد:</span>

                        <select 
                            className="flex-1 bg-slate-50 border border-slate-200 text-xs py-1.5 px-2 rounded-md font-bold text-slate-700 outline-none min-w-[150px]"
                            onChange={(e) => {
                                const val = e.target.value;
                                if(val) {
                                    const [fId, cId] = val.split('|');
                                    setValue(`fields.${fieldIndex}.conditions.${k}.trigger_field_id`, fId);
                                    setValue(`fields.${fieldIndex}.conditions.${k}.trigger_choice_id`, cId);
                                } else {
                                    setValue(`fields.${fieldIndex}.conditions.${k}.trigger_field_id`, "");
                                    setValue(`fields.${fieldIndex}.conditions.${k}.trigger_choice_id`, "");
                                }
                            }}
                            defaultValue={cond.trigger_field_id ? `${cond.trigger_field_id}|${cond.trigger_choice_id}` : ""}
                        >
                            <option value="">انتخاب فیلد و گزینه...</option>
                            {availableTriggers.map((trig, i) => (
                                <option key={i} value={`${trig.fieldId}|${trig.choiceId}`}>
                                    {trig.label}
                                </option>
                            ))}
                        </select>
                        
                        <span className="text-xs text-slate-500 font-medium">وضعیتش</span>

                        <select 
                            {...register(`fields.${fieldIndex}.conditions.${k}.operator`)}
                            className="bg-slate-50 border border-slate-200 text-xs py-1.5 px-2 rounded-md font-bold text-slate-700 outline-none"
                        >
                            <option value="equals">برابر باشد</option>
                            <option value="not_equals">مخالف باشد</option>
                            <option value="is_empty">خالی باشد</option>
                            <option value="is_not_empty">خالی نباشد</option>
                        </select>
                        
                        <button type="button" onClick={() => remove(k)} className="text-error/70 hover:text-error p-1.5 bg-red-50 hover:bg-red-100 rounded-md transition-colors ml-auto">
                            <Trash2 size={14}/>
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FieldConditions;