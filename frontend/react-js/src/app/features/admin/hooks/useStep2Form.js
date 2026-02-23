import { useMemo } from 'react';
import { useForm } from 'react-hook-form';

// تولید یک آیدی موقت که با فرمت API همخوانی داشته باشد
export const generateTempId = (prefix = 'temp') => {
    return `${prefix}_${Math.random().toString(36).substr(2, 9)}`;
};

export const useStep2Form = (initialData, onSave) => {
    
    // 🎯 آماده‌سازی دیتای اولیه: تزریق temp_id به موجودیت‌های جدید
    const mappedInitialData = useMemo(() => {
        // فرض می‌کنیم در معماری جدید، فیلدها در product.fields از سرور می‌آیند
        const fields = (initialData?.fields || []).map((field, fIndex) => ({
            id: field.id || null,
            temp_id: field.id ? null : (field.temp_id || generateTempId('field')),
            title: field.title || '',
            field_type: field.field_type || 'dropdown',
            is_required: Boolean(field.is_required),
            order: field.order || fIndex + 1,
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
        mode: 'onChange' // برای اعتبارسنجی در لحظه
    });

    // 🎯 ساخت پی‌لود نهایی دقیقاً طبق داکیومنت Swagger جدید
    const onSubmit = (formData) => {
        const cleanPayload = {
            fields: formData.fields.map((field, fIndex) => {
                const baseField = {
                    title: field.title,
                    field_type: field.field_type,
                    is_required: field.is_required,
                    order: fIndex + 1, // آپدیت خودکار ترتیب بر اساس ایندکس آرایه
                    choices: field.choices.map((choice, cIndex) => {
                        const baseChoice = {
                            title: choice.title,
                            numeric_value: String(choice.numeric_value || "0"),
                            order: cIndex + 1
                        };
                        // فقط یکی از این دو باید ارسال شود: id یا temp_id
                        if (choice.id) baseChoice.id = choice.id;
                        else baseChoice.temp_id = choice.temp_id;
                        return baseChoice;
                    }),
                    // پاکسازی و مپ کردن شروط وابستگی
                    conditions: field.conditions
                        .filter(cond => cond.trigger_field_id && cond.trigger_choice_id)
                        .map(cond => ({
                            trigger_field_id: cond.trigger_field_id,
                            operator: cond.operator || "equals",
                            trigger_choice_id: cond.trigger_choice_id,
                            action: cond.action || "show"
                        }))
                };

                // ثبت شناسه اصلی یا موقت برای خود فیلد
                if (field.id) baseField.id = field.id;
                else baseField.temp_id = field.temp_id;

                return baseField;
            })
        };

        console.log("🚀 Payload استپ ۲ (جدید):", JSON.stringify(cleanPayload, null, 2));
        if (onSave) onSave(cleanPayload);
    };

    return {
        methods,
        onSubmit: methods.handleSubmit(onSubmit)
    };
};