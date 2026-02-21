import { useEffect, useMemo, useState, createContext, useContext } from 'react';
import { useForm } from 'react-hook-form';
import { adminProductService } from '../services/adminProductService';

export const Step2Context = createContext({});
export const useStep2Data = () => useContext(Step2Context);

export const generateRefId = (prefix = 'temp') => {
    return `${prefix}_${Math.random().toString(36).substr(2, 6)}`;
};

export const useStep2Form = (productId, initialData, onSave) => {
    const [productQuantities, setProductQuantities] = useState([]);
    const [isLoadingQuantities, setIsLoadingQuantities] = useState(false);

    useEffect(() => {
        if (!productId || productId === 'new' || productId === 'undefined') return;

        const fetchQuantities = async () => {
            try {
                setIsLoadingQuantities(true);
                const data = await adminProductService.getProductQuantities(productId);
                if (Array.isArray(data) && data.length > 0) {
                    setProductQuantities(data);
                }
            } catch (error) {
                console.error("❌ خطا در دریافت تیراژها:", error);
            } finally {
                setIsLoadingQuantities(false);
            }
        };

        fetchQuantities();
    }, [productId]);

    // 🎯 حیاتی: اطمینان از اینکه تمام مقادیر (حتی اونایی که از بک‌اند میان) حتما ref_id دارن
    const mappedInitialData = useMemo(() => {
        if (!initialData || !initialData.options) return { options: [] };
        
        return {
            ...initialData,
            options: initialData.options.map(opt => ({
                ...opt,
                option_id: opt.option_id || opt.id || null, 
                values_config: (opt.choices || opt.values_config || []).map(val => ({
                    ...val,
                    // اگه از بک‌ند اومد و ref_id نداشت، با ایدی خودش یه ref_id براش میسازیم تا شروط کار کنه
                    ref_id: val.ref_id || (val.id ? `temp_${val.id}` : generateRefId('val')),
                    conditions: val.conditions || [],
                    quantity_prices: val.quantity_prices || []
                }))
            }))
        };
    }, [initialData]);

    const methods = useForm({
        defaultValues: mappedInitialData,
        mode: 'onChange'
    });

    useEffect(() => {
        if (initialData) methods.reset(mappedInitialData);
    }, [mappedInitialData, methods]);

    // 🎯 ساخت پی‌لود نهایی دقیقاً مو‌به‌مو طبق داکیومنت Word
    const onSubmit = (formData) => {
        const cleanPayload = {
            options: formData.options.map(opt => ({
                option_id: opt.option_id || null,
                name: opt.name,
                label: opt.label,
                input_type: opt.input_type,
                is_required: Boolean(opt.is_required),
                values_config: opt.values_config.map(val => ({
                    id: val.id || null,
                    ref_id: val.ref_id, // رفرنس آیدی اجباری
                    global_value_id: null, // طبق داکیومنت باید null باشد
                    label: val.label,
                    price_impact: Number(val.price_impact || 0),
                    is_default: Boolean(val.is_default),
                    quantity_prices: (val.quantity_prices || []).map(qp => ({
                        quantity_id: Number(qp.quantity_id),
                        price: Number(qp.price || 0)
                    })),
                    // شروط فقط در صورتی ارسال میشن که تارگت داشته باشن
                    conditions: (val.conditions || []).filter(c => c.required_ref_id).map(cond => ({
                        required_ref_id: cond.required_ref_id,
                        action: "show"
                    }))
                }))
            }))
        };

        console.log("🚀 Payload ارسالی به API:", JSON.stringify(cleanPayload, null, 2));
        if (onSave) onSave(cleanPayload);
    };

    return {
        methods,
        onSubmit: methods.handleSubmit(onSubmit),
        step2ContextValue: { productQuantities, isLoadingQuantities }
    };
};