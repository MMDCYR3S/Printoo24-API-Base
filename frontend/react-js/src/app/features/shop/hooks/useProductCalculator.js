// src/app/features/shop/hooks/useProductCalculator.js
import { useState, useEffect, useMemo, useCallback } from 'react';

export const useProductCalculator = (productData) => {
  // --- State ---
  const [quantityType, setQuantityType] = useState('fixed'); // 'fixed' | 'custom'
  const [selectedQuantityId, setSelectedQuantityId] = useState(''); 
  const [customQuantity, setCustomQuantity] = useState(1);

  const [sizeType, setSizeType] = useState('fixed'); // 'fixed' | 'custom'
  const [selectedSizeId, setSelectedSizeId] = useState('');
  const [customDimensions, setCustomDimensions] = useState({ width: '', height: '' });

  // برای آپشن‌ها: { [optionId]: choiceId }
  const [selectedOptions, setSelectedOptions] = useState({});

  // --- Initialization (دقیقا کد خودت) ---
  useEffect(() => {
    if (!productData) return;

    // 1. تنظیم اولیه تیراژ
    if (productData.quantities?.length > 0) {
      setQuantityType('fixed');
      // اولین گزینه را پیش‌فرض انتخاب کن
      setSelectedQuantityId(productData.quantities[0].id);
    } else {
      setQuantityType('custom');
      setCustomQuantity(productData.pricing_config?.min_quantity || 1);
    }

    // 2. تنظیم اولیه سایز
    if (productData.sizes?.length > 0) {
      setSizeType('fixed');
      setSelectedSizeId(productData.sizes[0].id);
    } else if (productData.pricing_config?.accepts_custom_dimensions) {
      setSizeType('custom');
    }

    // 3. تنظیم اولیه آپشن‌های اجباری (Default Options)
    if (productData.options?.length > 0) {
      const initialOptions = {};
      productData.options.forEach(opt => {
        const defaultChoice = opt.choices?.find(c => c.is_default);
        if (defaultChoice) {
          initialOptions[opt.id] = defaultChoice.id;
        } else if (opt.is_required && opt.choices?.length > 0) {
          // اگر دیفالت نداشت ولی اجباری بود، اولی رو انتخاب کن
          initialOptions[opt.id] = opt.choices[0].id;
        }
      });
      setSelectedOptions(initialOptions);
    }
  }, [productData?.product_info?.id]);

  // --- Calculation Logic (دقیقا کد خودت با نام pricing) ---
  const pricing = useMemo(() => {
    // مقادیر اولیه
    const result = { baseUnitPrice: 0, extraCosts: 0, finalUnitPrice: 0, finalQuantity: 1, totalPrice: 0 };
    if (!productData) return result;

    const basePrice = parseFloat(productData.product_info?.price) || 0;
    let extra = 0;

    // الف) محاسبه تاثیر سایز
    if (sizeType === 'fixed' && selectedSizeId) {
      const size = productData.sizes?.find(s => s.id == selectedSizeId);
      if (size?.price_impact) extra += parseFloat(size.price_impact);
    }

    // ب) محاسبه تاثیر آپشن‌ها
    if (productData.options?.length > 0) {
      productData.options.forEach(opt => {
        const choiceId = selectedOptions[opt.id];
        if (choiceId) {
          const choice = opt.choices?.find(c => c.id == choiceId);
          if (choice?.price_impact) extra += parseFloat(choice.price_impact);
        }
      });
    }

    // ج) تعیین تعداد نهایی
    let qty = 1;
    if (quantityType === 'fixed') {
      const qObj = productData.quantities?.find(q => q.id == selectedQuantityId);
      // طبق جیسون شما کلید quantity است
      qty = qObj?.quantity ? parseInt(qObj.quantity) : 1;
    } else {
      qty = parseInt(customQuantity) || 1;
    }

    const unitPrice = basePrice + extra;

    return {
      baseUnitPrice: basePrice,
      extraCosts: extra,
      finalUnitPrice: unitPrice,
      finalQuantity: qty,
      totalPrice: unitPrice * qty
    };
  }, [productData, quantityType, selectedQuantityId, customQuantity, sizeType, selectedSizeId, selectedOptions]);

  // --- متد جدید برای ساخت Payload (بدون تاثیر روی محاسبات قبلی) ---
  const getSubmitPayload = useCallback(() => {
    if (!productData) return null;

    const payload = {
      product_id: productData.product_info?.id || productData.id,
      options: selectedOptions,
      has_design: true 
    };

    if (quantityType === 'fixed') {
      payload.quantity_id = selectedQuantityId;
    } else {
      payload.quantity = parseInt(customQuantity);
    }

    if (sizeType === 'fixed') {
      payload.size_id = selectedSizeId;
    } else {
      payload.width = parseFloat(customDimensions.width);
      payload.height = parseFloat(customDimensions.height);
    }

    return payload;
  }, [productData, quantityType, selectedQuantityId, customQuantity, sizeType, selectedSizeId, customDimensions, selectedOptions]);

  return {
    state: { quantityType, selectedQuantityId, customQuantity, sizeType, selectedSizeId, customDimensions, selectedOptions },
    setters: { setQuantityType, setSelectedQuantityId, setCustomQuantity, setSizeType, setSelectedSizeId, setCustomDimensions, setSelectedOptions },
    pricing, // این همان نامی است که صفحه محصول انتظار دارد
    getSubmitPayload // این تابع جدید را فقط موقع کلیک دکمه صدا بزنید
  };
};