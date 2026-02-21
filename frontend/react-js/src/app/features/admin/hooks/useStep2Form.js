import { useEffect, useMemo } from 'react';
import { useForm } from 'react-hook-form';

// تابع کمکی برای تولید شناسه‌های موقت (ref_id) برای شروط و وابستگی‌ها
export const generateRefId = (prefix = 'ref') => {
    return `${prefix}_${Math.random().toString(36).substr(2, 8)}`;
};

export const useStep2Form = (initialData, onSave) => {
    // تبدیل دیتای بک‌اند به ساختاری که فرانت‌اند نیاز دارد
    const mappedInitialData = useMemo(() => {
        if (!initialData || !initialData.options) return { options: [] };
        
        return {
            ...initialData,
            options: initialData.options.map(opt => ({
                ...opt,
                product_option_id: opt.product_option_id || opt.id || null, 
                input_type: opt.type || opt.input_type || 'select',
                values_config: opt.choices || opt.values_config || []
            }))
        };
    }, [initialData]);

    // راه‌اندازی React Hook Form
    const methods = useForm({
        defaultValues: mappedInitialData,
        mode: 'onChange' // ولیدیشن در لحظه تایپ
    });

    const { reset, handleSubmit } = methods;

    // همگام‌سازی فرم در صورت تغییر دیتای اولیه (مثلاً بعد از فچ شدن از API)
    useEffect(() => {
        if (initialData) {
            reset(mappedInitialData);
        }
    }, [mappedInitialData, reset]);

    // مدیریت سابمیت نهایی فرم
    const onSubmit = (data) => {
        console.log("🚀 Payload آماده ارسال به بک‌اند:", data);
        if (onSave) {
            onSave(data);
        }
    };

    return {
        methods,
        onSubmit: handleSubmit(onSubmit),
    };
};