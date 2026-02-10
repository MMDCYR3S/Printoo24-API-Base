// src/app/features/admin/categories/CategoryUpsertPage.jsx
import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowRight, Save, Info, ListTree, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import clsx from 'clsx';

import { categorySchema } from '../dashboard/categorySchema';
import { adminCategoryService } from '../../services/adminCategoryService';
import ImageUploader from './components/ImageUploader';
import SubCategoryManager from './components/SubCategoryManager';

const CategoryUpsertPage = () => {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('info'); 

  // 1. دریافت دیتای اصلی
  const { data: categoryData, isLoading: isFetching } = useQuery({
    queryKey: ['category', id],
    queryFn: () => adminCategoryService.getById(id),
    enabled: isEdit,
  });

  // 2. دریافت لیست دسته‌ها (فقط ریشه‌ها برای انتخاب به عنوان والد)
  const { data: rootCategories = [] } = useQuery({
    queryKey: ['admin-categories-roots'],
    queryFn: () => adminCategoryService.getRoots(),
  });

  // تشخیص اینکه آیا این دسته خودش زیرمجموعه است؟ (اگر والد داشته باشد، زیرمجموعه است)
  // اگر زیرمجموعه باشد، نباید تب "زیرمجموعه‌ها" را ببیند.
  const isSubCategory = !!categoryData?.parent;

  const { 
    register, handleSubmit, setValue, reset, watch, formState: { errors } 
  } = useForm({
    resolver: zodResolver(categorySchema),
    defaultValues: { is_active: true }
  });

  // پر کردن فرم
  useEffect(() => {
    if (categoryData) {
      reset({
        name: categoryData.name,
        parent: categoryData.parent || '',
        description: categoryData.description || '',
        is_active: categoryData.is_active,
        banner_box: categoryData.banner_box,
      });
    }
  }, [categoryData, reset]);

  // Mutation
  const mutation = useMutation({
    mutationFn: (data) => {
      const formData = { ...data };
      
      // ✅ 1. افزودن User ID از لوکال استوریج
      const storedUserId = localStorage.getItem('userId');
      if (storedUserId) {
        formData.user = parseInt(storedUserId);
      } else {
        console.warn("User ID not found!");
      }

      // هندل کردن والد
      if (formData.parent === '' || formData.parent === '0') formData.parent = null;
      
      // هندل کردن عکس (اگر استرینگ بود یعنی تغییر نکرده، حذفش کن)
      if (typeof formData.banner_box === 'string') delete formData.banner_box;
      
      // ✅ 2. اطمینان از حذف Slug و Banner Wide
      delete formData.slug; 
      delete formData.banner_wide;

      return isEdit 
        ? adminCategoryService.update(id, formData)
        : adminCategoryService.create(formData);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['admin-categories']);
      toast.success(isEdit ? 'تغییرات ذخیره شد' : 'دسته ایجاد شد');
      
      if (!isEdit) {
        // اگر جدید بود و والد نداشت (ریشه بود)، برو برای افزودن زیردسته
        if (!data.parent) {
            navigate(`/admin/categories/edit/${data.id}`, { replace: true });
            setActiveTab('subs');
        } else {
            // اگر زیردسته ساختیم، برگرد به لیست
            navigate('/admin/categories');
        }
      }
    },
    onError: (err) => {
      console.error(err);
      toast.error('خطا در ارتباط با سرور');
    }
  });

  const onSubmit = (data) => mutation.mutate(data);

  // دیدن مقدار لحظه‌ای والد برای کنترل UI
  const watchedParent = watch('parent');

  if (isEdit && isFetching) return <div className="h-screen flex items-center justify-center"><span className="loading loading-spinner loading-lg text-primary"></span></div>;

  return (
    <div className="p-6 md:p-8 max-w-5xl mx-auto pb-24 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button onClick={() => navigate('/admin/categories')} className="btn btn-circle btn-ghost btn-sm">
          <ArrowRight size={20} />
        </button>
        <div>
          <h1 className="text-2xl font-black text-slate-800">
            {isEdit ? `ویرایش: ${categoryData?.name}` : 'افزودن دسته جدید'}
          </h1>
        </div>
      </div>

      {/* Tabs */}
      <div role="tablist" className="tabs tabs-boxed bg-white p-1 rounded-xl border border-slate-100 w-fit mb-8">
        <button 
            role="tab" 
            className={clsx("tab h-10 px-6 rounded-lg gap-2 transition-all", activeTab === 'info' && "bg-primary text-white shadow-md")}
            onClick={() => setActiveTab('info')}
        >
            <Info size={16}/> اطلاعات اصلی
        </button>
        
        {/* ✅ تب زیرمجموعه فقط اگر دسته والد باشد (Root) نشان داده می‌شود */}
        {(!watchedParent && !isSubCategory) && (
            <button 
                role="tab" 
                className={clsx("tab h-10 px-6 rounded-lg gap-2 transition-all", activeTab === 'subs' && "bg-primary text-white shadow-md")}
                onClick={() => setActiveTab('subs')}
                disabled={!isEdit} 
            >
                <ListTree size={16}/> زیرمجموعه‌ها
                {categoryData?.children?.length > 0 && <span className="badge badge-sm bg-white/20 text-current border-0 ml-1">{categoryData.children.length}</span>}
            </button>
        )}
      </div>

      {/* --- Tab 1: Info --- */}
      <div className={activeTab === 'info' ? 'block' : 'hidden'}>
        <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
              
              <div className="form-control mb-4">
                <label className="label font-bold text-slate-700 text-sm mb-2">نام دسته‌بندی <span className="text-error">*</span></label>
                <input 
                  {...register('name')}
                  className={`input input-bordered rounded-xl w-full ${errors.name ? 'input-error' : ''}`}
                />
                {errors.name && <span className="text-error text-xs mt-1">{errors.name.message}</span>}
              </div>

              <div className="form-control mb-4">
                <label className="label font-bold text-slate-700 text-sm mb-2">دسته والد</label>
                <select 
                  {...register('parent')} 
                  className="select select-bordered w-full rounded-xl"
                >
                  <option value="">-- دسته اصلی (Root) --</option>
                  {rootCategories
                      .filter(c => c.id !== Number(id)) // خودش را نشان نده
                      .map(c => (
                          <option key={c.id} value={c.id}>{c.name}</option>
                      ))
                  }
                </select>
                <label className="label text-xs text-slate-400">
                    اگر "دسته اصلی" باشد، می‌تواند زیرمجموعه داشته باشد. اگر والد انتخاب کنید، خودش زیرمجموعه می‌شود.
                </label>
              </div>

              <div className="form-control">
                <label className="label font-bold text-slate-700 text-sm mb-2">توضیحات</label>
                <textarea 
                  {...register('description')}
                  className="textarea textarea-bordered h-32 rounded-xl w-full" 
                ></textarea>
              </div>
            </div>
          </div>

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
                  label="تصویر شاخص (مربع)"
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

      {/* --- Tab 2: Sub Categories --- */}
      <div className={activeTab === 'subs' ? 'block' : 'hidden'}>
         {!isEdit ? (
             <div className="alert alert-info shadow-sm">
                <AlertCircle size={20}/>
                <span>برای افزودن زیرمجموعه، ابتدا دسته اصلی را ذخیره کنید.</span>
             </div>
         ) : isSubCategory ? (
             <div className="alert alert-warning shadow-sm">
                <AlertCircle size={20}/>
                <span>این دسته خودش یک زیرمجموعه است و نمی‌تواند زیرمجموعه دیگری داشته باشد.</span>
             </div>
         ) : (
             // نمایش کامپوننت مدیریت زیردسته‌ها فقط برای Rootها
             <SubCategoryManager parentCategory={categoryData} />
         )}
      </div>

    </div>
  );
};

export default CategoryUpsertPage;