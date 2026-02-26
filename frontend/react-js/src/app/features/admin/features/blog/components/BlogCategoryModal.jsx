import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { blogCategorySchema } from '../schemas/blogCategorySchema';
import { useCreateBlogCategory, useUpdateBlogCategory } from '../hooks/useBlogCategories';

const BlogCategoryModal = ({ isOpen, onClose, editData }) => {
  const isEditMode = !!editData;
  const createMutation = useCreateBlogCategory();
  const updateMutation = useUpdateBlogCategory();

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: yupResolver(blogCategorySchema),
    defaultValues: {
      name: '',
      is_active: true
    }
  });

  // پر کردن فرم در صورت باز شدن برای ویرایش
  useEffect(() => {
    if (editData) {
      reset({
        name: editData.name,
        is_active: editData.is_active
      });
    } else {
      reset({ name: '', is_active: true });
    }
  }, [editData, reset]);

  const onSubmit = (data) => {
    if (isEditMode) {
      updateMutation.mutate(
        { id: editData.id, data },
        { onSuccess: () => onClose() }
      );
    } else {
      createMutation.mutate(data, { onSuccess: () => onClose() });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">
          {isEditMode ? 'ویرایش دسته‌بندی' : 'ایجاد دسته‌بندی جدید'}
        </h2>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">نام دسته‌بندی</label>
            <input
              type="text"
              {...register('name')}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="مثال: آموزش‌های پیش از چاپ"
            />
            {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>}
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              {...register('is_active')}
              id="is_active"
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="is_active" className="ml-2 mr-2 block text-sm text-gray-900">
              وضعیت فعال باشد
            </label>
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              انصراف
            </button>
            <button
              type="submit"
              disabled={createMutation.isLoading || updateMutation.isLoading}
              className="px-4 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isEditMode ? 'ثبت تغییرات' : 'ایجاد دسته‌بندی'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BlogCategoryModal;