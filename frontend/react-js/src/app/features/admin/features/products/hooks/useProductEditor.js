// src/app/features/admin/products/hooks/useProductEditor.js
import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { adminProductService } from '../services/adminProductService';

export const useProductEditor = () => {
  const { id } = useParams(); // اگر ID باشد یعنی حالت ویرایش
  const isEditMode = !!id;
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  // استیت برای مدیریت تب‌ها (مراحل)
  const [activeTab, setActiveTab] = useState('basic'); // basic | options | media

  // 1. دریافت دیتای محصول (اگر در حالت ویرایش باشیم)
  const { data: product, isLoading: isFetching } = useQuery({
    queryKey: ['admin-product', id],
    queryFn: () => adminProductService.getById(id),
    enabled: isEditMode,
    staleTime: 0, 
  });

  // 2. میوتیشن مرحله ۱ (ساخت/ویرایش هسته)
  const step1Mutation = useMutation({
    mutationFn: (data) => {
      return isEditMode 
        ? adminProductService.update(id, data) 
        : adminProductService.create(data);
    },
    onSuccess: (data) => {
      // 🛠️ اصلاح مهم: سرور در حالت ساخت، مستقیم {id: 76} برمی‌گرداند
      const newProductId = data.id || data.shell?.id; 
      const targetId = isEditMode ? id : newProductId;

      if (!targetId) {
        console.error("Create Response:", data);
        toast.error("خطا در دریافت شناسه محصول جدید");
        return;
      }

      toast.success(isEditMode ? 'اطلاعات پایه بروز شد' : 'محصول با موفقیت ایجاد شد');
      
      // اگر محصول جدید بود، ریدایرکت کن به صفحه ویرایش همین محصول
      if (!isEditMode) {
         navigate(`/admin/products/edit/${targetId}`, { replace: true });
         // بعد از نویگیت، با کمی تاخیر تب را ببر روی آپشن‌ها
         setTimeout(() => setActiveTab('options'), 100);
      } else {
         queryClient.invalidateQueries(['admin-product', id]);
         setActiveTab('options');
      }
    },
    onError: (err) => {
      console.error(err);
      // نمایش خطای سرور اگر موجود باشد
      const serverMsg = err.response?.data?.message || err.response?.data?.detail;
      toast.error(serverMsg || 'خطا در ذخیره اطلاعات پایه.');
    }
  });

  // 3. میوتیشن مرحله ۲ (سینک آپشن‌ها)
  const step2Mutation = useMutation({
    mutationFn: (payload) => adminProductService.syncOptions(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-product', id]);
      toast.success('ویژگی‌های محصول ذخیره شد');
      setActiveTab('media'); // برو مرحله تصاویر
    },
    onError: () => toast.error('خطا در ذخیره ویژگی‌ها')
  });

  // 4. میوتیشن آپلود تصویر (تکی)
  const uploadImageMutation = useMutation({
    mutationFn: (formData) => adminProductService.uploadImage(id, formData),
    onError: () => toast.error('آپلود ناموفق بود')
  });

  // 5. میوتیشن مرحله ۳ (نهایی‌سازی مدیا)
  const step3Mutation = useMutation({
    mutationFn: (payload) => adminProductService.syncMedia(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-product', id]);
      toast.success('تصاویر و فایل‌ها مرتب‌سازی شدند');
      navigate('/admin/products'); // بازگشت به لیست
    }
  });

  return {
    isEditMode,
    productId: id,
    product,
    isLoading: isFetching,
    
    // مدیریت تب‌ها
    activeTab,
    setActiveTab,

    // اکشن‌ها
    saveStep1: step1Mutation.mutate,
    isSavingStep1: step1Mutation.isPending,

    saveStep2: step2Mutation.mutate,
    isSavingStep2: step2Mutation.isPending,

    uploadImage: uploadImageMutation.mutateAsync, 
    isUploading: uploadImageMutation.isPending,

    saveStep3: step3Mutation.mutate,
    isSavingStep3: step3Mutation.isPending,
  };
};