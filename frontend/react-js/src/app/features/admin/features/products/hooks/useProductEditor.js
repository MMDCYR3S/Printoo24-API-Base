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
    // تبدیل مقادیر فرم به فرمت دقیق JSON
    return {
      shell: {
        name: formData.shell.name,
        category_id: Number(formData.shell.category_id), // تبدیل به عدد (حیاتی)
        description: formData.shell.description || "",
        has_price: true, // طبق مثال همیشه true
        price: String(formData.shell.price || "0"),
        has_quantity: formData.shell.has_quantity,
        is_active: formData.shell.is_active,
        guide_text: formData.shell.guide_text || "",
        guide_type: formData.shell.guide_type || "info"
      },
      pricing_config: {
        base_setup_price: Number(formData.pricing_config.base_setup_price || 0),
        design_service_available: formData.pricing_config.design_service_available,
        design_fee: Number(formData.pricing_config.design_fee || 0),
        // اگر تیراژدار نیست، مینیمم و ماکسیمم را بفرست
        ...( !formData.shell.has_quantity && {
            min_quantity: Number(formData.pricing_config.min_quantity || 1),
            max_quantity: formData.pricing_config.max_quantity ? Number(formData.pricing_config.max_quantity) : null
        })
      },
      // آرایه quantities فقط شامل id و guide (طبق مثال)
      quantities: formData.quantities?.map(q => ({
        id: Number(q.id),
        guide_text: q.guide_text || "",
        guide_type: q.guide_type || "info"
      })) || [],
      // آرایه sizes
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
      
      // اگر در حالت ادیت هستیم، متد update، اگر جدید است create
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
         // ریدایرکت به صفحه ویرایش محصول جدید
         navigate(`/admin/products/edit/${targetId}`, { replace: true });
         // رفتن به تب بعدی
         setTimeout(() => setActiveTab('options'), 500);
      } else {
         queryClient.invalidateQueries(['admin-product', id]);
         setActiveTab('options');
      }
    },
    onError: (err) => {
      console.error("Save Error:", err);
      // نمایش خطای دقیق سرور
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

  // توابع آپلود مدیا (جداگانه برای استفاده در کامپوننت مدیا)
  const uploadImageMutation = useMutation({
    mutationFn: (formData) => adminProductService.uploadImage(id, formData),
  });

  const uploadAttachmentMutation = useMutation({
    mutationFn: (formData) => adminProductService.uploadAttachment(formData),
  });

  // ذخیره نهایی (در واقع همان آپدیت مرحله ۱ است که شامل مدیا هم می‌شود اگر در Payload باشد)
  // اما چون مدیا جدا آپلود می‌شود، اینجا فقط برای تغییر وضعیت نهایی یا ریدایرکت استفاده می‌شود
  const finalSaveMutation = useMutation({
    mutationFn: async (payload) => {
        // اینجا می‌توان یک درخواست نهایی آپدیت زد که مثلاً وضعیت را فعال کند
        // فعلاً فقط ریدایرکت می‌کنیم چون آپلودها انجام شده‌اند
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

    // اکسپوز کردن توابع آپلود
    uploadImageAsync: uploadImageMutation.mutateAsync, 
    uploadAttachmentAsync: uploadAttachmentMutation.mutateAsync,
    isUploading: uploadImageMutation.isPending || uploadAttachmentMutation.isPending,

    saveStep3: finalSaveMutation.mutate,
    isSavingStep3: finalSaveMutation.isPending,
  };
};