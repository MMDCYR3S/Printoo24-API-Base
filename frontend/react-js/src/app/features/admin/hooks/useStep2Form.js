import { useMemo } from 'react';
import { useForm } from 'react-hook-form';

export const generateTempId = (prefix = 'temp') => {
    return `${prefix}_${Math.random().toString(36).substr(2, 9)}`;
};

export const useStep2Form = (initialData, onSave) => {
    
    const mappedInitialData = useMemo(() => {
        const fields = (initialData?.fields || []).map((field, fIndex) => ({
            id: field.id || null,
            temp_id: field.id ? null : (field.temp_id || generateTempId('field')),
            title: field.title || '',
            field_type: field.field_type || 'dropdown',
            is_required: Boolean(field.is_required),
            order: field.order || fIndex + 1,
            multi_select_operator: field.multi_select_operator || 'add', // جدید
            choices: (field.choices || []).map((choice, cIndex) => ({
                id: choice.id || null,
                temp_id: choice.id ? null : (choice.temp_id || generateTempId('choice')),
                title: choice.title || '',
                numeric_value: choice.numeric_value || "0",
                order: choice.order || cIndex + 1
            })),
            conditions: field.conditions || []
        }));

        return { fields };
    }, [initialData]);

    const methods = useForm({
        defaultValues: mappedInitialData,
        mode: 'onChange' 
    });

    const onSubmit = (formData) => {
        const cleanPayload = {
            fields: formData.fields.map((field, fIndex) => {
                const baseField = {
                    title: field.title,
                    field_type: field.field_type,
                    is_required: field.is_required,
                    order: fIndex + 1,
                    // ارسال عملگر داخلی فقط اگر فیلد چندانتخابی باشد
                    ...(field.field_type === 'multi_select' && { multi_select_operator: field.multi_select_operator }),
                    
                    // ارسال گزینه‌ها فقط برای فیلدهای انتخابی
                    choices: ['dropdown', 'single_select', 'multi_select'].includes(field.field_type) 
                        ? field.choices.map((choice, cIndex) => {
                            const baseChoice = {
                                title: choice.title,
                                numeric_value: String(choice.numeric_value || "0"),
                                order: cIndex + 1
                            };
                            if (choice.id) baseChoice.id = choice.id;
                            else baseChoice.temp_id = choice.temp_id;
                            return baseChoice;
                        })
                        : [],

                    // 🎯 رفع باگ شروط: مپ کردن دقیق طبق سواگر
                    conditions: field.conditions
                        .filter(cond => cond.trigger_field_id) 
                        .map(cond => ({
                            trigger_field_id: cond.trigger_field_id,
                            operator: cond.operator || "equals",
                            trigger_choice_id: cond.trigger_choice_id || null,
                            action: cond.action || "show"
                        }))
                };

                if (field.id) baseField.id = field.id;
                else baseField.temp_id = field.temp_id;

                return baseField;
            })
        };

        console.log("🚀 Payload استپ ۲:", JSON.stringify(cleanPayload, null, 2));
        if (onSave) onSave(cleanPayload);
    };

    return {
        methods,
        onSubmit: methods.handleSubmit(onSubmit)
    };
};