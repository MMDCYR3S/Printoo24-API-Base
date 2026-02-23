import React from 'react';
import { useFormContext, useFieldArray, useWatch } from 'react-hook-form';
import { Plus, Trash2, Link2 } from 'lucide-react';

const FieldConditions = ({ fieldIndex }) => {
    const { control, register } = useFormContext();
    const allFields = useWatch({ control, name: 'fields' }) || [];
    
    const { fields: condFields, append, remove } = useFieldArray({
        control,
        name: `fields.${fieldIndex}.conditions`
    });

    // استخراج تمام فیلدها و گزینه‌های "قبلی" برای ساخت منوی دراپ‌داون شروط
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

    if (availableTriggers.length === 0) return null; // اگر فیلد قبلی وجود ندارد، شرطی هم نمی‌توان گذاشت

    return (
        <div className="bg-blue-50/50 p-4 rounded-xl border border-blue-100 mt-4">
            <div className="flex justify-between items-center mb-3">
                <span className="text-xs font-extrabold text-blue-800 flex items-center gap-1.5"><Link2 size={14}/> شروط نمایش این فیلد</span>
                <button type="button" onClick={() => append({ trigger_field_id: "", trigger_choice_id: "", operator: "equals", action: "show" })} className="text-[10px] text-blue-600 font-bold hover:underline">
                    + افزودن وابستگی
                </button>
            </div>
            
            <div className="space-y-2">
                {condFields.map((cond, k) => (
                    <div key={cond.id} className="flex gap-2 items-center bg-white p-2 rounded-lg border border-blue-100">
                        <span className="text-[10px] text-slate-500 font-bold">نمایش بده اگر:</span>
                        
                        {/* چون ساختار دیتابیس trigger_field_id و trigger_choice_id رو جدا می‌خواد،
                          ما تو فرانت یک value ترکیبی می‌سازیم و موقع انتخاب جداش می‌کنیم.
                        */}
                        <select 
                            className="flex-1 bg-transparent border-b border-slate-200 text-xs py-1 outline-none"
                            onChange={(e) => {
                                const [fId, cId] = e.target.value.split('|');
                                // آپدیت دستی مقادیر در فرم
                                methods.setValue(`fields.${fieldIndex}.conditions.${k}.trigger_field_id`, fId);
                                methods.setValue(`fields.${fieldIndex}.conditions.${k}.trigger_choice_id`, cId);
                            }}
                            defaultValue={cond.trigger_field_id ? `${cond.trigger_field_id}|${cond.trigger_choice_id}` : ""}
                        >
                            <option value="">انتخاب کنید...</option>
                            {availableTriggers.map((trig, i) => (
                                <option key={i} value={`${trig.fieldId}|${trig.choiceId}`}>
                                    {trig.label}
                                </option>
                            ))}
                        </select>
                        
                        <input type="hidden" {...register(`fields.${fieldIndex}.conditions.${k}.operator`)} value="equals" />
                        <input type="hidden" {...register(`fields.${fieldIndex}.conditions.${k}.action`)} value="show" />
                        
                        <button type="button" onClick={() => remove(k)} className="text-error/70 hover:text-error p-1"><Trash2 size={14}/></button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FieldConditions;