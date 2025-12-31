// src/app/features/shop/hooks/useProductCalculator.js
import { useState, useEffect, useMemo } from 'react';

export const useProductCalculator = (productData) => {
  // استیت‌های فرم
  const [quantityType, setQuantityType] = useState('fixed'); // 'fixed' | 'custom'
  const [selectedQuantityId, setSelectedQuantityId] = useState(null); // برای تیراژ
  const [customQuantity, setCustomQuantity] = useState(1); // برای تعداد دستی

  const [sizeType, setSizeType] = useState('fixed'); // 'fixed' | 'custom'
  const [selectedSizeId, setSelectedSizeId] = useState(null);
  const [customDimensions, setCustomDimensions] = useState({ width: '', height: '' });

  const [selectedOptions, setSelectedOptions] = useState({}); // { optionId: choiceId }

  // ۱. تعیین نوع ورودی تعداد (تیراژ یا دستی)
  useEffect(() => {
    if (productData) {
      if (productData.quantities && productData.quantities.length > 0) {
        setQuantityType('fixed');
        setSelectedQuantityId(productData.quantities[0].id); // پیش‌فرض اولی
      } else {
        setQuantityType('custom');
        setCustomQuantity(productData.pricing_config?.min_quantity || 1);
      }

      // تنظیم پیش‌فرض سایز
      if (productData.sizes && productData.sizes.length > 0) {
        setSelectedSizeId(productData.sizes[0].id);
      }
    }
  }, [productData]);

  // ۲. محاسبه قیمت لحظه‌ای
  const pricing = useMemo(() => {
    if (!productData) return { unitPrice: 0, totalPrice: 0, extraCosts: 0 };

    let baseUnitPrice = parseFloat(productData.product_info.price) || 0;
    let extraCosts = 0; // هزینه‌های اضافه شده به واحد

    // الف) محاسبه تاثیر سایز
    if (sizeType === 'fixed' && selectedSizeId) {
      const size = productData.sizes.find(s => s.id === parseInt(selectedSizeId));
      if (size && size.price_impact) {
        extraCosts += parseFloat(size.price_impact);
      }
    }
    // (برای سایز دلخواه اگر فرمولی دارید اینجا اضافه می‌شود، فعلا پایه در نظر گرفته شده)

    // ب) محاسبه تاثیر آپشن‌ها
    if (productData.options) {
        productData.options.forEach(opt => {
            const choiceId = selectedOptions[opt.id];
            if (choiceId) {
                const choice = opt.choices.find(c => c.id === parseInt(choiceId));
                if (choice && choice.price_impact) {
                    extraCosts += parseFloat(choice.price_impact);
                }
            } else if (opt.choices) {
                // اگر انتخابی نکرده، چک کنیم پیش‌فرضی دارد؟ (معمولا در UI هندل میشه)
                const defaultChoice = opt.choices.find(c => c.is_default);
                if(defaultChoice) {
                   // اینجا می‌توانیم لاجیک پیش‌فرض را هندل کنیم ولی بهتر است در UI ست شود
                }
            }
        });
    }

    const finalUnitPrice = baseUnitPrice + extraCosts;

    // ج) تعیین تعداد نهایی
    let finalQuantity = 1;
    if (quantityType === 'fixed') {
      const qtyObj = productData.quantities?.find(q => q.id === parseInt(selectedQuantityId));
      finalQuantity = qtyObj ? qtyObj.value : 1; // فرض بر اینکه آبجکت تیراژ فیلد value دارد
    } else {
      finalQuantity = parseInt(customQuantity) || 1;
    }

    return {
      baseUnitPrice,
      extraCosts,
      finalUnitPrice,
      finalQuantity,
      totalPrice: finalUnitPrice * finalQuantity
    };
  }, [productData, quantityType, selectedQuantityId, customQuantity, sizeType, selectedSizeId, selectedOptions]);

  return {
    state: { quantityType, selectedQuantityId, customQuantity, sizeType, selectedSizeId, customDimensions, selectedOptions },
    setters: { setQuantityType, setSelectedQuantityId, setCustomQuantity, setSizeType, setSelectedSizeId, setCustomDimensions, setSelectedOptions },
    pricing
  };
};