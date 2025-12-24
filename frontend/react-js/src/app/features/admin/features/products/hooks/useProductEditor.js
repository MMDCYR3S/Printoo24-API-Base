import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { adminProductService } from '../../../services/adminProductService';

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
    staleTime: 0, // همیشه دیتای تازه بگیر برای ادیت
  });

  // 2. میوتیشن مرحله ۱ (ساخت/ویرایش هسته)
  const step1Mutation = useMutation({
    mutationFn: (data) => {
      return isEditMode 
        ? adminProductService.update(id, data) 
        : adminProductService.create(data);
    },
    onSuccess: (data) => {
      const productId = isEditMode ? id : data.shell.id; // گرفتن آیدی محصول ساخته شده
      toast.success(isEditMode ? 'اطلاعات پایه بروز شد' : 'محصول با موفقیت ایجاد شد');
      
      // اگر محصول جدید بود، ریدایرکت کن به صفحه ویرایش همین محصول (برای ادامه مراحل)
      if (!isEditMode) {
         navigate(`/dashboard/products/edit/${productId}`, { replace: true });
         // بعد از نویگیت، تب را ببر روی آپشن‌ها
         setTimeout(() => setActiveTab('options'), 100);
      } else {
         // در حالت ویرایش، فقط دیتای کش را آپدیت کن
         queryClient.invalidateQueries(['admin-product', id]);
         // برو مرحله بعد (اختیاری)
         setActiveTab('options');
      }
    },
    onError: (err) => {
      console.error(err);
      toast.error('خطا در ذخیره اطلاعات پایه. لطفا ورودی‌ها را چک کنید.');
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
      navigate('/dashboard/products'); // بازگشت به لیست
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

    uploadImage: uploadImageMutation.mutateAsync, // Async برای اینکه منتظر آپلود بمونیم
    isUploading: uploadImageMutation.isPending,

    saveStep3: step3Mutation.mutate,
    isSavingStep3: step3Mutation.isPending,
  };
};