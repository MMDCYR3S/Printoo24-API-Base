// src/app/features/admin/products/hooks/useProductEditor.js
import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { adminProductService } from '../../../services/adminProductService';

export const useProductEditor = () => {
  const { id } = useParams();
  const isEditMode = !!id;
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [activeTab, setActiveTab] = useState('basic');

  // دریافت محصول برای ویرایش
  const { 
    data: product, 
    isLoading: isQueryLoading, 
    isError, 
    error: queryError 
  } = useQuery({
    queryKey: ['admin-product', id],
    queryFn: () => adminProductService.getById(id),
    enabled: isEditMode,
    retry: 1,
    staleTime: 0, 
  });

  const isLoading = isEditMode ? isQueryLoading : false;

  // --- ساخت Payload طبق مستندات API ---
  const prepareStep1Payload = (formData) => {
    const isTirazhi = formData.shell.has_quantity; // وضعیت تیراژی یا تعدادی

    // 1. ساختن کانفیگ قیمت پایه (مشترک بین هر دو حالت)
    const pricingConfig = {
      base_setup_price: Number(formData.pricing_config.base_setup_price || 0),
      design_service_available: formData.pricing_config.design_service_available || false,
      design_fee: Number(formData.pricing_config.design_fee || 0),
    };

    // 2. اعمال فیلدهای اختصاصی حالت تعدادی/متری
    if (!isTirazhi) {
      // این مقادیر از فرم خوانده می‌شوند (با پیش‌فرض‌های امن)
      pricingConfig.allow_custom_quantity = formData.pricing_config.allow_custom_quantity ?? true;
      pricingConfig.min_quantity = Number(formData.pricing_config.min_quantity || 1);
      
      if (formData.pricing_config.max_quantity) {
        pricingConfig.max_quantity = Number(formData.pricing_config.max_quantity);
      }
      
      // اگر در فرم، ابعاد سفارشی هندل شده بود اینجا اضافه می‌شود
      if (formData.pricing_config.accepts_custom_dimensions) {
         pricingConfig.accepts_custom_dimensions = formData.pricing_config.accepts_custom_dimensions;
         pricingConfig.min_width = Number(formData.pricing_config.min_width || 0);
         pricingConfig.max_width = Number(formData.pricing_config.max_width || 0);
      }
    }

    return {
      shell: {
        name: formData.shell.name,
        category_id: Number(formData.shell.category_id), // تبدیل به عدد (حیاتی)
        description: formData.shell.description || "",
        has_price: true, // طبق داکیومنت همیشه true است
        
        show_price: String(formData.shell.show_price || "0"),

        // 🔴 منطق قیمت پایه: اگر تیراژی است 0 می‌رود، در غیر این صورت قیمت وارد شده
        price: isTirazhi ? "0" : String(formData.shell.price || "0"),
        
        has_quantity: isTirazhi,
        
        // اگر تعدادی/متری است، معمولاً price_per_unit باید ست شود (طبق داکیومنت سواگر)
        ...(!isTirazhi && { price_per_unit: 1 }), 

        is_active: formData.shell.is_active,
        guide_text: formData.shell.guide_text || "",
        guide_type: formData.shell.guide_type || "info"
      },
      
      pricing_config: pricingConfig,
      
      // 🔴 منطق تیراژها: اگر تعدادی است، آرایه خالی می‌شود تا دیتای سرور پاک شود.
      // اگر تیراژی است، مپ می‌شود و فیلد "price" حتماً ارسال می‌گردد.
      quantities: isTirazhi 
        ? (formData.quantities?.map(q => ({
            id: Number(q.id),
            price: Number(q.price || 0), // این فیلد در نسخه قبل جا افتاده بود
            guide_text: q.guide_text || "",
            guide_type: q.guide_type || "info"
          })) || [])
        : [],
      
      // آرایه sizes (بدون تغییر، مستقل از استراتژی قیمت‌گذاری)
      sizes: formData.sizes?.map(s => ({
        id: Number(s.id),
        price_impact: Number(s.price_impact || 0),
        guide_text: s.guide_text || "",
        guide_type: s.guide_type || "info"
      })) || []
    };
  };

  // --- Mutation Step 1 ---
  const step1Mutation = useMutation({
    mutationFn: (rawFormData) => {
      const payload = prepareStep1Payload(rawFormData);
      
      return isEditMode 
        ? adminProductService.update(id, payload) 
        : adminProductService.create(payload);
    },
    onSuccess: (data) => {
      const targetId = isEditMode ? id : (data.id || data.shell?.id);
      
      if (!targetId) {
         toast.error("خطا: شناسه محصول بازگردانده نشد");
         return;
      }

      toast.success(isEditMode ? 'تغییرات ذخیره شد' : 'محصول با موفقیت ایجاد شد');

      if (!isEditMode) {
         navigate(`/admin/products/edit/${targetId}`, { replace: true });
         setTimeout(() => setActiveTab('options'), 500);
      } else {
         queryClient.invalidateQueries(['admin-product', id]);
         setActiveTab('options');
      }
    },
    onError: (err) => {
      console.error("Save Error:", err);
      const msg = err.response?.data?.message || err.response?.data?.detail;
      if (msg) {
          toast.error(`خطا: ${JSON.stringify(msg)}`);
      } else {
          toast.error('خطا در ذخیره اطلاعات. لطفاً ورودی‌ها را بررسی کنید.');
      }
    }
  });

  // --- Other Mutations ---
  const step2Mutation = useMutation({
    mutationFn: (payload) => adminProductService.syncOptions(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-product', id]);
      toast.success('ویژگی‌ها ذخیره شد');
      setActiveTab('media');
    },
    onError: () => toast.error('خطا در ذخیره ویژگی‌ها')
  });

  const uploadImageMutation = useMutation({
    mutationFn: (formData) => adminProductService.uploadImage(id, formData),
  });

  const uploadAttachmentMutation = useMutation({
    mutationFn: (formData) => adminProductService.uploadAttachment(formData),
  });

  const finalSaveMutation = useMutation({
    mutationFn: async (payload) => {
        return true; 
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-product', id]);
      toast.success('مراحل ویرایش تمام شد');
      navigate('/admin/products');
    }
  });

  return {
    isEditMode,
    productId: id,
    product, // این دیتا همون چیزیه که تو فرم برای Edit لود میشه
    isLoading,
    isError,
    queryError,
    
    activeTab,
    setActiveTab,

    saveStep1: step1Mutation.mutate,
    isSavingStep1: step1Mutation.isPending,

    saveStep2: step2Mutation.mutate,
    isSavingStep2: step2Mutation.isPending,

    uploadImageAsync: uploadImageMutation.mutateAsync, 
    uploadAttachmentAsync: uploadAttachmentMutation.mutateAsync,
    isUploading: uploadImageMutation.isPending || uploadAttachmentMutation.isPending,

    saveStep3: finalSaveMutation.mutate,
    isSavingStep3: finalSaveMutation.isPending,
  };
};