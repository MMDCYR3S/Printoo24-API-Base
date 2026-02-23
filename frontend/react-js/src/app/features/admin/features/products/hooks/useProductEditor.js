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

  // 🎯 آماده‌سازی پی‌لود استپ ۱ طبق داکیومنت جدید بک‌اند
  const prepareStep1Payload = (formData) => {
    const s = formData.shell;
    
    const payload = {
      shell: {
        name: s.name,
        // ارسال مستقیم آیدی پدر و فرزند
        category_id: s.category_id ? Number(s.category_id) : null,
        subcategory_id: s.subcategory_id ? Number(s.subcategory_id) : null,
        
        description: s.description || "",
        has_price: Boolean(s.has_price),
        
        // قیمت همیشه 0، بقیه مقادیر از فرم
        price: "0",
        show_price: s.has_price ? String(s.show_price || "0") : "0",
        price_per_unit: s.has_price ? Number(s.price_per_unit || 0) : 0,
        
        has_quantity: Boolean(s.has_quantity),
        is_active: Boolean(s.is_active),
        
        guide_text: s.guide_text || "",
        guide_type: s.guide_type || "info"
      }
    };

    // اضافه کردن مین و مکس در صورت تعدادی بودن
    if (payload.shell.has_quantity) {
        payload.shell.min_quantity = Number(s.min_quantity || 1);
        if (s.max_quantity) {
            payload.shell.max_quantity = Number(s.max_quantity);
        }
    }

    return payload;
  };

  const step1Mutation = useMutation({
    mutationFn: (rawFormData) => {
      const payload = prepareStep1Payload(rawFormData);
      console.log("🚀 Payload ارسالی استپ ۱:", JSON.stringify(payload, null, 2));
      // گفتی این API نقش همه رو بازی میکنه، پس هم تو کریت و هم تو آپدیت میشه همینو فرستاد
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

      toast.success(isEditMode ? 'اطلاعات پایه ذخیره شد' : 'هسته محصول ایجاد شد');

      if (!isEditMode) {
         navigate(`/admin/products/edit/${targetId}`, { replace: true });
         setTimeout(() => setActiveTab('fields'), 500);
      } else {
         queryClient.invalidateQueries(['admin-product', id]);
         setActiveTab('fields');
      }
    },
    onError: (err) => {
      const msg = err.response?.data?.message || err.response?.data?.detail;
      toast.error(msg ? `خطا: ${JSON.stringify(msg)}` : 'خطا در ذخیره اطلاعات پایه');
    }
  });

  const step2Mutation = useMutation({
    mutationFn: (payload) => adminProductService.syncFields(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-product', id]);
      toast.success('ساختار فرم ذخیره شد');
      setActiveTab('formulas'); 
    },
    onError: () => toast.error('خطا در ذخیره فیلدها')
  });

  const step3Mutation = useMutation({
    mutationFn: (payload) => adminProductService.syncFormulas(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-product', id]);
      toast.success('فرمول‌های قیمت‌گذاری ذخیره شد');
      setActiveTab('media'); 
    },
    onError: () => toast.error('خطا در ذخیره فرمول‌ها')
  });

  const uploadImageMutation = useMutation({
    mutationFn: (formData) => adminProductService.uploadImage(id, formData),
  });

  const uploadAttachmentMutation = useMutation({
    mutationFn: (formData) => adminProductService.uploadAttachment(formData),
  });

  return {
    isEditMode,
    productId: id,
    product,
    isLoading,
    isError,
    queryError,
    
    activeTab,
    setActiveTab,

    saveStep1: step1Mutation.mutate,
    isSavingStep1: step1Mutation.isPending,

    saveStep2: step2Mutation.mutate,
    isSavingStep2: step2Mutation.isPending,

    saveStep3: step3Mutation.mutate,
    isSavingStep3: step3Mutation.isPending,

    uploadImageAsync: uploadImageMutation.mutateAsync, 
    uploadAttachmentAsync: uploadAttachmentMutation.mutateAsync,
    isUploading: uploadImageMutation.isPending || uploadAttachmentMutation.isPending,
  };
};