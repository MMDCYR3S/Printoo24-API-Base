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
  
  // شروع همیشه از تب اول است
  const [activeTab, setActiveTab] = useState('basic');

  // دریافت اطلاعات کامل محصول برای حالت ویرایش
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

  // --- Step 1: Core (اطلاعات پایه) ---
  const step1Mutation = useMutation({
    mutationFn: (payload) => {
      // پی‌لود این مرحله از ProductStep1Form میاد (همان لاجیک قبلی که دادی درسته)
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

      toast.success(isEditMode ? 'اطلاعات پایه ذخیره شد' : 'محصول ایجاد شد');

      if (!isEditMode) {
         navigate(`/admin/products/edit/${targetId}`, { replace: true });
         setTimeout(() => setActiveTab('fields'), 500); // هدایت به مرحله ۲
      } else {
         queryClient.invalidateQueries(['admin-product', id]);
         setActiveTab('fields');
      }
    },
    onError: (err) => toast.error('خطا در ذخیره اطلاعات پایه')
  });

  // --- Step 2: Sync Fields (همگام‌سازی فیلدها) ---
  const step2Mutation = useMutation({
    mutationFn: (payload) => adminProductService.syncFields(id, payload),
    onSuccess: () => {
      // 🎯 بعد از ذخیره فیلدها، باید دیتای محصول رفرش بشه تا id های واقعی رو بگیریم
      queryClient.invalidateQueries(['admin-product', id]);
      toast.success('ساختار فرم ذخیره شد');
      setActiveTab('formulas'); // هدایت به فرمول‌ساز
    },
    onError: () => toast.error('خطا در ذخیره فیلدها')
  });

  // --- Step 3: Sync Formulas (فرمول‌ساز) ---
  const step3Mutation = useMutation({
    mutationFn: (payload) => adminProductService.syncFormulas(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-product', id]);
      toast.success('فرمول‌های قیمت‌گذاری ذخیره شد');
      setActiveTab('media'); // هدایت به بخش رسانه
    },
    onError: () => toast.error('خطا در ذخیره فرمول‌ها')
  });

  // --- Step 4: Media ---
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