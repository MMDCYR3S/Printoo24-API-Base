// src/app/features/admin/categories/CategoryUpsertPage.jsx
import React, { useEffect } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowRight, Save, Globe, Info } from 'lucide-react';
import toast from 'react-hot-toast';

import { categorySchema } from '../dashboard/categorySchema';
import { adminCategoryService } from '../../services/adminCategoryService';
import ImageUploader from './components/ImageUploader';

const CategoryUpsertPage = () => {
  const { id } = useParams(); // اگر آی‌دی باشد یعنی حالت ویرایش
  const isEdit = !!id;
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // 1. دریافت دیتای اصلی (در صورت ویرایش)
  const { data: categoryData, isLoading: isFetching } = useQuery({
    queryKey: ['category', id],
    queryFn: () => adminCategoryService.getById(id),
    enabled: isEdit,
  });

  // 2. دریافت لیست دسته‌ها (برای انتخاب والد)
  const { data: allCategories = [] } = useQuery({
    queryKey: ['admin-categories-list'],
    queryFn: () => adminCategoryService.getAll(),
  });

  // 3. تنظیمات فرم
  const { 
    register, handleSubmit, setValue, control, reset, formState: { errors }, watch 
  } = useForm({
    resolver: zodResolver(categorySchema),
    defaultValues: { is_active: true }
  });

  // پر کردن فرم بعد از دریافت دیتا
  useEffect(() => {
    if (categoryData) {
      reset({
        name: categoryData.name,
        slug: categoryData.slug,
        parent: categoryData.parent || '',
        description: categoryData.description || '',
        is_active: categoryData.is_active,
        banner_box: categoryData.banner_box, // URL
        banner_wide: categoryData.banner_wide, // URL
      });
    }
  }, [categoryData, reset]);

  // 4. Mutation ذخیره‌سازی
  const mutation = useMutation({
    mutationFn: (data) => {
      const formData = { ...data };
      if (formData.parent === '') formData.parent = null;
      
      // نکته مهم: اگر فایل استرینگ بود (یعنی عکس قبلی)، از فرم دیتا حذفش می‌کنیم تا سرور ارور ندهد
      // یا سرور باید هندل کند. معمولا ارسال نکردن بهتر است.
      if (typeof formData.banner_box === 'string') delete formData.banner_box;
      if (typeof formData.banner_wide === 'string') delete formData.banner_wide;

      return isEdit 
        ? adminCategoryService.update(id, formData)
        : adminCategoryService.create(formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-categories']);
      toast.success(isEdit ? 'دسته‌بندی با موفقیت به‌روز شد' : 'دسته‌بندی جدید ساخته شد');
      navigate('/admin/categories');
    },
    onError: (err) => {
      console.error(err);
      toast.error('خطا در ذخیره‌سازی اطلاعات');
    }
  });

  const onSubmit = (data) => mutation.mutate(data);

  // برای SEO Preview
  const watchedName = watch('name');
  const watchedDesc = watch('description');
  const watchedSlug = watch('slug');

  if (isEdit && isFetching) return <div className="h-screen flex items-center justify-center"><span className="loading loading-spinner loading-lg text-primary"></span></div>;

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto pb-24">
      {/* --- HEADER --- */}
      <div className="flex items-center gap-4 mb-8">
        <button onClick={() => navigate(-1)} className="btn btn-circle btn-ghost btn-sm">
          <ArrowRight size={20} />
        </button>
        <div>
          <h1 className="text-2xl font-black text-slate-800">
            {isEdit ? 'ویرایش دسته‌بندی' : 'افزودن دسته جدید'}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            اطلاعات پایه، تصاویر و تنظیمات سئو را وارد کنید
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* === ستون اصلی (چپ - اطلاعات متنی) === */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Card: Basic Info */}
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
            <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
              <Info size={18} className="text-primary"/>
              اطلاعات پایه
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Name */}
              <div className="form-control">
                <label className="label font-bold text-slate-700 text-sm mb-2">نام دسته‌بندی <span className="text-error">*</span></label>
                <input 
                  {...register('name')}
                  type="text" 
                  className={`input input-bordered rounded-xl focus:border-primary w-full ${errors.name ? 'input-error' : ''}`}
                  placeholder="مثال: کارت ویزیت"
                />
                {errors.name && <span className="text-error text-xs mt-1">{errors.name.message}</span>}
              </div>

              {/* Slug */}
              <div className="form-control">
                <label className="label font-bold text-slate-700 text-sm mb-2">
                  نامک (URL) <span className="text-error">*</span>
                </label>
                <input 
                  {...register('slug')}
                  type="text" 
                  className={`input input-bordered rounded-xl focus:border-primary dir-ltr font-mono text-sm w-full ${errors.slug ? 'input-error' : ''}`}
                  placeholder="business-card"
                />
                <label className="label text-[10px] text-slate-400">
                   فقط حروف انگلیسی، اعداد و خط تیره (-)
                </label>
                {errors.slug && <span className="text-error text-xs mt-1">{errors.slug.message}</span>}
              </div>
            </div>

            {/* Parent Selector */}
            <div className="form-control mt-6">
              <label className="label font-bold text-slate-700 text-sm mb-2">دسته‌بندی والد</label>
              <select 
                {...register('parent')} 
                className="select select-bordered w-full rounded-xl focus:border-primary"
              >
                <option value="">-- بدون والد (دسته اصلی) --</option>
                {allCategories
                  .filter(c => c.id !== Number(id)) // جلوگیری از انتخاب خود به عنوان والد
                  .map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
              <label className="label text-xs text-slate-400">
                 اگر این دسته زیرمجموعه دسته دیگری است، آن را انتخاب کنید.
              </label>
            </div>

            {/* Description */}
            <div className="form-control mt-6">
              <label className="label font-bold text-slate-700 text-sm mb-2">توضیحات (Meta Description)</label>
              <br/>
              <textarea 
                {...register('description')}
                className="textarea textarea-bordered h-32 rounded-xl focus:border-primary text-base w-full" 
                placeholder="توضیحاتی کوتاه درباره این دسته‌بندی بنویسید..."
              ></textarea>
              {errors.description && <span className="text-error text-xs mt-1">{errors.description.message}</span>}
            </div>
          </div>

          {/* Card: SEO Preview (Wow Factor) */}
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
            <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Globe size={18} className="text-blue-500"/>
              پیش‌نمایش گوگل (SEO)
            </h3>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
               <div className="font-sans" dir="ltr">
                  <div className="text-sm text-slate-500 mb-1 flex items-center gap-1">
                     printoo24.com <span className="text-slate-400">› categories › {watchedSlug || 'your-slug'}</span>
                  </div>
                  <div className="text-xl text-[#1a0dab] hover:underline cursor-pointer truncate font-medium">
                     {watchedName ? `خرید و قیمت ${watchedName} | پرینتو24` : 'عنوان صفحه دسته‌بندی'}
                  </div>
                  <div className="text-sm text-slate-600 mt-1 line-clamp-2">
                     {watchedDesc || 'این توضیحات همان متنی است که در کادر بالا وارد می‌کنید و در نتایج گوگل نمایش داده می‌شود. سعی کنید از کلمات کلیدی مناسب استفاده کنید.'}
                  </div>
               </div>
            </div>
          </div>

        </div>

        {/* === ستون کناری (راست - مدیا و وضعیت) === */}
        <div className="space-y-6">
          
          {/* Status Card */}
          <div className="bg-white p-5 rounded-3xl shadow-sm border border-slate-100">
             <div className="form-control">
                <label className="label cursor-pointer">
                  <span className="label-text font-bold text-slate-700">وضعیت انتشار</span>
                  <input 
                    type="checkbox" 
                    className="toggle toggle-success toggle-lg" 
                    {...register('is_active')}
                  />
                </label>
                <p className="text-xs text-slate-400 mt-2 px-1">
                   در صورت غیرفعال بودن، این دسته در سایت نمایش داده نمی‌شود.
                </p>
             </div>
          </div>

          {/* Media Card */}
          <div className="bg-white p-5 rounded-3xl shadow-sm border border-slate-100 space-y-6">
            <h3 className="font-bold text-slate-800 border-b border-slate-100 pb-3">تصاویر</h3>
            
            {/* Box Banner */}
            <div>
               <ImageUploader 
                  label="تصویر شاخص (مربعی)"
                  defaultImage={categoryData?.banner_box}
                  onChange={(file) => setValue('banner_box', file, { shouldValidate: true })}
                  error={errors.banner_box}
                  aspectRatio="square"
               />
               <p className="text-[10px] text-slate-400 mt-1">سایز پیشنهادی: 600x600 پیکسل</p>
            </div>

            {/* Wide Banner */}
            <div>
               <ImageUploader 
                  label="بنر عریض (صفحه آرشیو)"
                  defaultImage={categoryData?.banner_wide}
                  onChange={(file) => setValue('banner_wide', file, { shouldValidate: true })}
                  error={errors.banner_wide}
                  aspectRatio="wide"
               />
               <p className="text-[10px] text-slate-400 mt-1">سایز پیشنهادی: 1920x400 پیکسل</p>
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="sticky top-6">
            <button 
                type="submit" 
                disabled={mutation.isPending}
                className="btn btn-primary w-full shadow-xl shadow-primary/20 rounded-xl h-12 text-lg font-bold"
            >
                {mutation.isPending ? <span className="loading loading-dots"></span> : (
                    <>
                       <Save size={20}/>
                       {isEdit ? 'ذخیره تغییرات' : 'انتشار دسته‌بندی'}
                    </>
                )}
            </button>
          </div>

        </div>
      </form>
    </div>
  );
};

export default CategoryUpsertPage;