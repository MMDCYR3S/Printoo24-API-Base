import { useState, useEffect, useMemo, useCallback } from 'react';
import debounce from 'lodash/debounce';
import { shopService } from '../../../services/shopService';

export const useProductCalculator = (productData) => {
  const [selectedOptions, setSelectedOptions] = useState({});
  const [livePrice, setLivePrice] = useState(0);
  const [isCalculating, setIsCalculating] = useState(false);
  const [priceError, setPriceError] = useState(null);

  // ۱. مقداردهی اولیه دیفالت‌ها
  useEffect(() => {
    if (!productData || !Array.isArray(productData.fields)) return;

    setSelectedOptions(prev => {
      const newState = { ...prev };
      let hasChanges = false;
      productData.fields.forEach(field => {
        if (newState[field.id] === undefined && Array.isArray(field.choices) && field.choices.length > 0) {
          const defaultChoice = field.choices.find(c => c.is_default) || field.choices[0];
          if (defaultChoice) {
            newState[field.id] = String(defaultChoice.id); // حتما استرینگ باشه طبق داکیومنت
            hasChanges = true;
          }
        }
      });
      return hasChanges ? newState : prev;
    });

    // قیمت اولیه برای نمایش تا قبل از لود شدن از سرور
    setLivePrice(parseFloat(productData?.show_price || 0));
  }, [productData]);

  // ۲. منطق نمایش فیلدها (همچنان سمت فرانت نیازه تا فیلدای نامربوط مخفی بشن)
  const visibleFields = useMemo(() => {
    if (!productData || !Array.isArray(productData.fields)) return [];
    return productData.fields.filter(field => {
      if (!Array.isArray(field.conditions) || field.conditions.length === 0) return true;
      return field.conditions.every(cond => {
        if (cond.action === 'show' && cond.operator === 'equals') {
          return String(selectedOptions[cond.trigger_field_id]) === String(cond.trigger_choice_id);
        }
        return true;
      });
    }).map(f => f.id);
  }, [productData, selectedOptions]);

  // ۳. ریکوئست به بک‌اند با Debounce (جلوگیری از اسپم ریکوئست)
  const fetchPriceFromServer = useCallback(
    debounce(async (productId, currentSelections, visible) => {
      if (!productId) return;

      // فقط آپشن‌هایی که واقعاً تو صفحه دارن نمایش داده میشن رو بفرستیم به سرور (پاک کردن دیتای کثیف)
      const activeSelections = {};
      Object.entries(currentSelections).forEach(([fieldId, choiceId]) => {
        if (visible.includes(Number(fieldId))) {
          activeSelections[String(fieldId)] = String(choiceId);
        }
      });

      try {
        setIsCalculating(true);
        setPriceError(null);
        const result = await shopService.calculateLivePrice(productId, activeSelections);
        
        if (result?.success && result?.data) {
          setLivePrice(result.data.final_price);
        } else if (result?.success === false) {
          setPriceError(result.error);
        }
      } catch (error) {
        console.error("Live Price API Error:", error);
        setPriceError(error?.response?.data?.error || "خطا در ارتباط با سرور");
      } finally {
        setIsCalculating(false);
      }
    }, 400), // 400 میلی‌ثانیه دی‌باونس
    []
  );

  // ۴. هربار که کاربر روی مستطیل‌ها کلیک کرد، قیمت رو لایو بگیر
  useEffect(() => {
    if (productData?.id && Object.keys(selectedOptions).length > 0) {
      fetchPriceFromServer(productData.id, selectedOptions, visibleFields);
    }
  }, [selectedOptions, productData?.id, visibleFields, fetchPriceFromServer]);

  // آپدیت کردن استیت با کلیک کاربر روی فرم
  const handleOptionSelect = useCallback((fieldId, choiceId) => {
    setSelectedOptions(prev => ({ ...prev, [fieldId]: String(choiceId) }));
  }, []);

  // آماده کردن دیتای نهایی برای افزودن به سبد خرید
  const getSubmitPayload = useCallback(() => {
    const activeSelections = {};
    Object.entries(selectedOptions).forEach(([fieldId, choiceId]) => {
      if (visibleFields.includes(Number(fieldId))) {
        activeSelections[String(fieldId)] = String(choiceId);
      }
    });
    return {
      product_id: productData?.id,
      options: activeSelections
    };
  }, [productData, selectedOptions, visibleFields]);

  return {
    state: { selectedOptions, visibleFields },
    setters: { handleOptionSelect },
    pricing: { totalPrice: livePrice, isCalculating, error: priceError },
    getSubmitPayload
  };
};