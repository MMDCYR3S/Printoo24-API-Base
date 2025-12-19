// src/app/features/dashboard/categories/CategoryModal.jsx
import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X } from 'lucide-react';
import toast from 'react-hot-toast';
import { categorySchema } from '../dashboard/categorySchema';
import { adminCategoryService } from '../../services/adminCategoryService';

const CategoryModal = ({ isOpen, onClose, category, categories }) => {
  const queryClient = useQueryClient();
  const isEdit = !!category;

  const { register, handleSubmit, reset, formState: { errors, isSubmitting }, setValue, watch } = useForm({
    resolver: zodResolver(categorySchema),
    defaultValues: {
      name: '',
      slug: '',
      parent: '',
      description: '',
      is_active: true,
      banner_box: null, // فایل جدید
    },
  });

  // پر کردن فرم در حالت ویرایش
  useEffect(() => {
    if (category) {
      reset({
        name: category.name,
        slug: category.slug,
        parent: category.parent || '',
        description: category.description || '',
        is_active: category.is_active,
      });
      // نکته: فایل‌ها را نمی‌توانیم مقداردهی اولیه کنیم، فقط نمایش می‌دهیم
    } else {
      reset({ is_active: true });
    }
  }, [category, reset]);

  // Mutation
  const mutation = useMutation({
    mutationFn: (data) => {
        // تبدیل parent خالی به null برای ارسال به بک‌اند
        const finalData = { ...data, parent: data.parent === '' ? null : data.parent };
        return isEdit 
            ? adminCategoryService.update(category.id, finalData) 
            : adminCategoryService.create(finalData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-categories']);
      toast.success(isEdit ? 'دسته‌بندی ویرایش شد' : 'دسته‌بندی ایجاد شد');
      onClose();
    },
    onError: (err) => {
      console.error(err);
      toast.error('خطا در ذخیره اطلاعات');
    }
  });

  const onSubmit = (data) => {
    // اگر فایل انتخاب نشده باشد، مقدار آن را از آبجکت حذف می‌کنیم تا undefined ارسال نشود (مخصوصا در ادیت)
    const formData = { ...data };
    if (formData.banner_box instanceof FileList) {
        formData.banner_box = formData.banner_box[0];
    }
    mutation.mutate(formData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col">
        
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h3 className="text-lg font-bold text-gray-800">
            {isEdit ? `ویرایش دسته: ${category.name}` : 'افزودن دسته جدید'}
          </h3>
          <button onClick={onClose} className="btn btn-sm btn-circle btn-ghost">
            <X size={20} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4 flex-1 overflow-y-auto">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Name */}
            <div className="form-control">
              <label className="label text-sm font-medium">نام دسته‌بندی</label>
              <input 
                {...register('name')}
                type="text" 
                className={`input input-bordered ${errors.name ? 'input-error' : ''}`}
                placeholder="مثال: کارت ویزیت"
              />
              {errors.name && <span className="text-error text-xs mt-1">{errors.name.message}</span>}
            </div>

            {/* Slug */}
            <div className="form-control">
              <label className="label text-sm font-medium">نامک (Slug URL)</label>
              <input 
                {...register('slug')}
                type="text" 
                className={`input input-bordered dir-ltr font-mono text-sm ${errors.slug ? 'input-error' : ''}`}
                placeholder="visit-card"
              />
              {errors.slug && <span className="text-error text-xs mt-1">{errors.slug.message}</span>}
            </div>
          </div>

          {/* Parent Category */}
          <div className="form-control">
            <label className="label text-sm font-medium">دسته مادر</label>
            <select 
              {...register('parent')} 
              className="select select-bordered w-full"
            >
              <option value="">بدون والد (دسته اصلی)</option>
              {categories
                .filter(c => c.id !== category?.id) // خود دسته نمی‌تواند والد خودش باشد
                .map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div className="form-control">
            <label className="label text-sm font-medium">توضیحات (Meta Description)</label>
            <textarea 
              {...register('description')}
              className="textarea textarea-bordered h-24" 
              placeholder="توضیحات برای سئو و نمایش در سایت..."
            ></textarea>
          </div>

          {/* Image Upload */}
          <div className="form-control">
            <label className="label text-sm font-medium">تصویر مربعی (Box Banner)</label>
            <input 
              type="file" 
              accept="image/*"
              className="file-input file-input-bordered w-full" 
              {...register('banner_box')}
            />
            {category?.banner_box && !watch('banner_box')?.length && (
              <div className="mt-2 text-xs text-info flex items-center gap-2">
                <span>تصویر فعلی:</span>
                <a href={category.banner_box} target="_blank" className="link underline">مشاهده</a>
              </div>
            )}
            {errors.banner_box && <span className="text-error text-xs mt-1">{errors.banner_box.message}</span>}
          </div>

          {/* Active Toggle */}
          <div className="form-control w-fit">
            <label className="label cursor-pointer gap-3">
              <input 
                type="checkbox" 
                className="toggle toggle-success" 
                {...register('is_active')}
              />
              <span className="label-text font-medium">دسته‌بندی فعال باشد</span>
            </label>
          </div>

        </form>

        {/* Footer */}
        <div className="p-5 border-t border-gray-100 bg-gray-50 flex justify-end gap-3 rounded-b-2xl">
          <button 
            type="button" 
            onClick={onClose}
            className="btn btn-ghost"
            disabled={mutation.isPending}
          >
            انصراف
          </button>
          <button 
            type="submit" 
            onClick={handleSubmit(onSubmit)}
            className="btn btn-primary px-8"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? <span className="loading loading-spinner"></span> : (isEdit ? 'ذخیره تغییرات' : 'ایجاد دسته‌بندی')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CategoryModal;