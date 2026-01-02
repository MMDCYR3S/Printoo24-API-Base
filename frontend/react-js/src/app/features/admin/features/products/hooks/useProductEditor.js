// src/app/features/admin/products/hooks/useProductEditor.js
import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { adminProductService } from '../../../services/adminProductService';

export const useProductEditor = () => {
  const { id } = useParams();
  const isEditMode = !!id; // اگر ID باشد، یعنی ویرایش
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [activeTab, setActiveTab] = useState('basic');

  // --- 1. دریافت دیتای محصول (فقط در ویرایش) ---
  const { 
    data: product, 
    isLoading: isQueryLoading, 
    isError,              // ✅ اضافه شد: تشخیص خطا
    error: queryError     // ✅ اضافه شد: متن خطا
  } = useQuery({
    queryKey: ['admin-product', id],
    queryFn: () => adminProductService.getById(id),
    enabled: isEditMode, // فقط وقتی ID داریم درخواست بزن
    retry: 1,            // اگر فچ نشد، فقط 1 بار تلاش مجدد کن
    staleTime: 0, 
  });

  // اگر در حالت "ساخت" هستیم، لودینگ نداریم. اگر "ویرایش" هستیم، وضعیت کوئری مهم است.
  const isLoading = isEditMode ? isQueryLoading : false;

  // --- تابع تبدیل دیتا برای ارسال به سرور ---
  const preparePayload = (formData) => {
    return {
      ...formData,
      shell: {
        ...formData.shell,
        category_id: formData.shell.category_id ? Number(formData.shell.category_id) : null,
        price: String(formData.shell.price || "0"),
      },
      pricing_config: {
        ...formData.pricing_config,
        base_setup_price: Number(formData.pricing_config.base_setup_price || 0),
        design_fee: Number(formData.pricing_config.design_fee || 0),
        min_quantity: Number(formData.pricing_config.min_quantity || 1),
      },
      sizes: formData.sizes?.map(s => ({
        ...s,
        id: Number(s.id),
        price_impact: Number(s.price_impact || 0)
      })) || [],
      quantities: formData.quantities?.map(q => ({
        ...q,
        id: Number(q.id)
      })) || []
    };
  };

  // --- 2. میوتیشن ذخیره (Create / Update) ---
  const step1Mutation = useMutation({
    mutationFn: (rawFormData) => {
      const payload = preparePayload(rawFormData);
      return isEditMode 
        ? adminProductService.update(id, payload) 
        : adminProductService.create(payload);
    },
    onSuccess: (data) => {
      const targetId = isEditMode ? id : (data.id || data.shell?.id);
      
      if (!targetId) {
        toast.error("خطا: شناسه محصول دریافت نشد");
        return;
      }

      toast.success(isEditMode ? 'تغییرات ذخیره شد' : 'محصول ایجاد شد');

      if (!isEditMode) {
         // ریدایرکت به صفحه ویرایش
         navigate(`/admin/products/edit/${targetId}`, { replace: true });
         // بعد از نیم ثانیه برو تب بعدی
         setTimeout(() => setActiveTab('options'), 500);
      } else {
         queryClient.invalidateQueries(['admin-product', id]);
         setActiveTab('options');
      }
    },
    onError: (err) => {
      console.error("Save Error:", err);
      const msg = err.response?.data?.message || err.response?.data?.detail || 'خطا در ذخیره اطلاعات';
      toast.error(typeof msg === 'string' ? msg : 'خطای اعتبار سنجی فرم');
    }
  });

  // --- سایر میوتیشن‌ها ---
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
    onError: () => toast.error('آپلود ناموفق بود')
  });

  const step3Mutation = useMutation({
    mutationFn: (payload) => adminProductService.syncMedia(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-product', id]);
      toast.success('پایان مراحل ویرایش');
      navigate('/admin/products');
    }
  });

  return {
    isEditMode,
    productId: id,
    product,
    isLoading,
    isError,      // ✅ برگشت وضعیت خطا
    queryError,   // ✅ برگشت متن خطا
    
    activeTab,
    setActiveTab,

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