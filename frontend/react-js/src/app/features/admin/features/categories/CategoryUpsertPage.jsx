// src/app/features/admin/categories/CategoryUpsertPage.jsx
import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowRight, Save, Info } from 'lucide-react';
import toast from 'react-hot-toast';

import { categorySchema } from '../dashboard/categorySchema';
import { adminCategoryService } from '../../services/adminCategoryService';
import ImageUploader from './components/ImageUploader';

const CategoryUpsertPage = () => {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // 1. دریافت دیتای اصلی
  const { data: categoryData, isLoading: isFetching } = useQuery({
    queryKey: ['category', id],
    queryFn: () => adminCategoryService.getById(id),
    enabled: isEdit,
  });

  // 2. دریافت لیست دسته‌ها (برای والد)
  const { data: allCategories = [] } = useQuery({
    queryKey: ['admin-categories-list'],
    queryFn: () => adminCategoryService.getRoots ? adminCategoryService.getRoots() : adminCategoryService.getAll(),
  });

  // 3. تنظیمات فرم
  const { 
    register, handleSubmit, setValue, reset, formState: { errors } 
  } = useForm({
    resolver: zodResolver(categorySchema),
    defaultValues: { is_active: true }
  });

  useEffect(() => {
    if (categoryData) {
      reset({
        name: categoryData.name,
        // slug را اگر بک‌اند فرستاد در فرم نمی‌گذاریم یا فقط نمایش می‌دهیم
        parent: categoryData.parent || '',
        description: categoryData.description || '',
        is_active: categoryData.is_active,
        banner_box: categoryData.banner_box,
      });
    }
  }, [categoryData, reset]);

  // 4. Mutation
  const mutation = useMutation({
    mutationFn: (data) => {
      const formData = { ...data };
      if (formData.parent === '') formData.parent = null;
      if (typeof formData.banner_box === 'string') delete formData.banner_box;
      
      // پاکسازی فیلدهای احتمالی اضافه
      delete formData.slug; 
      delete formData.banner_wide;

      return isEdit 
        ? adminCategoryService.update(id, formData)
        : adminCategoryService.create(formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-categories']);
      toast.success(isEdit ? 'تغییرات ذخیره شد' : 'دسته جدید ایجاد شد');
      navigate('/admin/categories');
    },
    onError: (err) => {
      console.error("API Error:", err);
      toast.error('خطا در ارتباط با سرور');
    }
  });

  // هندلر خطا برای دیباگ کردن دکمه ذخیره
  const onInvalid = (errors) => {
    console.error("Validation Errors:", errors);
    toast.error('لطفاً خطاهای فرم را برطرف کنید');
  };

  const onSubmit = (data) => mutation.mutate(data);

  if (isEdit && isFetching) return <div className="h-screen flex items-center justify-center"><span className="loading loading-spinner loading-lg text-primary"></span></div>;

  return (
    <div className="p-6 md:p-8 max-w-5xl mx-auto pb-24">
      <div className="flex items-center gap-4 mb-8">
        <button onClick={() => navigate('/admin/categories')} className="btn btn-circle btn-ghost btn-sm">
          <ArrowRight size={20} />
        </button>
        <div>
          <h1 className="text-2xl font-black text-slate-800">
            {isEdit ? 'ویرایش دسته‌بندی' : 'افزودن دسته جدید'}
          </h1>
        </div>
      </div>

      {/* اضافه کردن onInvalid برای لاگ گرفتن ارورها */}
      <form onSubmit={handleSubmit(onSubmit, onInvalid)} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* === ستون اصلی === */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
            <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
              <Info size={18} className="text-primary"/>
              اطلاعات پایه
            </h3>
            
            {/* نام */}
            <div className="form-control mb-4">
              <label className="label font-bold text-slate-700 text-sm mb-2">نام دسته‌بندی <span className="text-error">*</span></label>
              <input 
                {...register('name')}
                type="text" 
                className={`input input-bordered rounded-xl w-full ${errors.name ? 'input-error' : ''}`}
                placeholder="نام دسته..."
              />
              {errors.name && <span className="text-error text-xs mt-1">{errors.name.message}</span>}
            </div>

            {/* Slug حذف شد */}

            {/* والد */}
            <div className="form-control mb-4">
              <label className="label font-bold text-slate-700 text-sm mb-2">دسته‌بندی والد</label>
              <select 
                {...register('parent')} 
                className="select select-bordered w-full rounded-xl"
              >
                <option value="">-- دسته اصلی (Root) --</option>
                {allCategories
                    .filter(c => c.id !== Number(id))
                    .map(c => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                    ))
                }
              </select>
            </div>

            {/* توضیحات */}
            <div className="form-control">
              <label className="label font-bold text-slate-700 text-sm mb-2">توضیحات</label>
              <textarea 
                {...register('description')}
                className="textarea textarea-bordered h-32 rounded-xl w-full" 
                placeholder="توضیحات اختیاری..."
              ></textarea>
            </div>
          </div>
        </div>

        {/* === ستون کناری === */}
        <div className="space-y-6">
          <div className="bg-white p-5 rounded-3xl shadow-sm border border-slate-100">
             <div className="form-control">
                <label className="label cursor-pointer">
                  <span className="label-text font-bold text-slate-700">وضعیت انتشار</span>
                  <input type="checkbox" className="toggle toggle-success" {...register('is_active')}/>
                </label>
             </div>
          </div>

          <div className="bg-white p-5 rounded-3xl shadow-sm border border-slate-100">
            <h3 className="font-bold text-slate-800 border-b border-slate-100 pb-3 mb-4">تصویر</h3>
            <ImageUploader 
                label="تصویر شاخص"
                defaultImage={categoryData?.banner_box}
                onChange={(file) => setValue('banner_box', file, { shouldValidate: true })}
                error={errors.banner_box}
                aspectRatio="square"
            />
          </div>
          
          <button 
              type="submit" 
              disabled={mutation.isPending}
              className="btn btn-primary w-full shadow-xl rounded-xl h-12 text-lg font-bold"
          >
              {mutation.isPending ? <span className="loading loading-dots"></span> : <><Save size={20}/> ذخیره</>}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CategoryUpsertPage;