import { useEffect, useMemo, useState, createContext, useContext } from 'react';
import { useForm } from 'react-hook-form';

// 👇 ایمپورت کردن سرویس خودت دقیقاً مثل فایل useProductEditor.js 👇
import { adminProductService } from '../services/adminProductService';

export const Step2Context = createContext({});
export const useStep2Data = () => useContext(Step2Context);

export const generateRefId = (prefix = 'ref') => {
    return `${prefix}_${Math.random().toString(36).substr(2, 8)}`;
};

export const useStep2Form = (productId, initialData, onSave) => {
    const [productQuantities, setProductQuantities] = useState([]);
    const [isLoadingQuantities, setIsLoadingQuantities] = useState(false);

    // فچ کردن تیراژها با استفاده از apiClient خودت
    useEffect(() => {
        if (!productId || productId === 'new' || productId === 'undefined') {
            return;
        }

        const fetchQuantities = async () => {
            try {
                setIsLoadingQuantities(true);
                
                // 🎯 الان دیگه از فایل سرویس خودت میره و توکن‌ها رو apiClient هندل میکنه
                const data = await adminProductService.getProductQuantities(productId);
                
                if (Array.isArray(data) && data.length > 0) {
                    setProductQuantities(data);
                }
            } catch (error) {
                console.error("❌ خطا در دریافت تیراژها از سرویس:", error);
            } finally {
                setIsLoadingQuantities(false);
            }
        };

        fetchQuantities();
    }, [productId]);

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

    const methods = useForm({
        defaultValues: mappedInitialData,
        mode: 'onChange'
    });

    const { reset, handleSubmit } = methods;

    useEffect(() => {
        if (initialData) reset(mappedInitialData);
    }, [mappedInitialData, reset]);

    const onSubmit = (data) => {
        if (onSave) onSave(data);
    };

    return {
        methods,
        onSubmit: handleSubmit(onSubmit),
        step2ContextValue: { productQuantities, isLoadingQuantities }
    };
};