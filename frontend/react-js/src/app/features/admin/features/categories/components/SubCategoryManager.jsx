// src/app/features/admin/categories/components/SubCategoryManager.jsx
import React, { useEffect, useRef } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2, Save, CornerDownRight, CheckCircle2, AlertCircle, Image as ImageIcon, Upload } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminCategoryService } from '../../../services/adminCategoryService';

const SubCategoryManager = ({ parentCategory }) => {
  const queryClient = useQueryClient();
  const parentSlug = parentCategory?.slug; 
  
  // رفرنس برای ذخیره URL های پیش‌نمایش جهت پاکسازی از مموری مرورگر
  const previewUrls = useRef([]);

  const { control, register, handleSubmit, reset, setValue, watch, formState: { isDirty } } = useForm({
    defaultValues: { subs: [] }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "subs"
  });

  // دریافت مقادیر لحظه‌ای فیلدها برای مانیتور کردن آدرس تصاویر پیش‌نمایش
  const subsWatch = watch("subs") || [];

  useEffect(() => {
    if (parentCategory?.children) {
      const formattedData = parentCategory.children.map(child => {
        // استخراج دقیق آدرس عکس از ساختار دیتای سرور
        const serverImg = child.banners?.box || child.banner_box || null;
        
        return {
          id: child.id,
          name: child.name,
          is_active: child.is_active ?? true,
          preview_url: serverImg, // تنظیم آدرس عکس سرور به عنوان پیش‌نمایش اولیه
          banner_box_file: null   // فایل باینری جدید در ابتدا خالی است
        };
      });
      reset({ subs: formattedData });
    }

    // Cleanup function برای جلوگیری از Memory Leak
    return () => {
      previewUrls.current.forEach(url => URL.revokeObjectURL(url));
    };
  }, [parentCategory, reset]);

  // هندل کردن انتخاب فایل جدید برای هر سطر
  const handleFileChange = (e, index) => {
    const file = e.target.files[0];
    if (file) {
      // ۱. ذخیره فایل باینری در فیلد مربوط به خودش
      setValue(`subs.${index}.banner_box_file`, file, { shouldDirty: true });
      
      // ۲. ساخت URL پیش‌نمایش لوکال و بروزرسانی فیلد preview_url
      const objectUrl = URL.createObjectURL(file);
      previewUrls.current.push(objectUrl);
      setValue(`subs.${index}.preview_url`, objectUrl, { shouldDirty: true });
    }
  };

  const bulkMutation = useMutation({
    mutationFn: (data) => {
      const formData = new FormData();

      data.subs.forEach((item, index) => {
        const prefix = `[${index}]`;

        formData.append(`${prefix}name`, item.name);
        formData.append(`${prefix}is_active`, item.is_active);
        formData.append(`${prefix}parent_slug`, parentSlug);

        if (item.id) {
          formData.append(`${prefix}id`, item.id);
        }

        // فقط در صورتی که فایل جدید انتخاب شده باشد فرستاده می‌شود
        if (item.banner_box_file) {
          formData.append(`${prefix}banner_box`, item.banner_box_file);
        }
      });

      return adminCategoryService.bulkUpsert(formData);
    },
    onSuccess: () => {
      // اینولید کردن کش کامپوننت والد برای لود مجدد دیتای تازه از سرور
      queryClient.invalidateQueries(['category', String(parentCategory.id)]);
      toast.success('زیرمجموعه‌ها با موفقیت ذخیره شدند');
    },
    onError: (err) => {
      console.error(err);
      toast.error('خطا در ذخیره زیردسته‌ها');
    }
  });

  const onSubmit = (data) => {
    if (!parentSlug) {
      toast.error('خطا: اسلاگ دسته والد یافت نشد!');
      return;
    }
    if (data.subs.length === 0 && fields.length === 0) {
        toast('لیست خالی است');
        return;
    }
    bulkMutation.mutate(data);
  };

  return (
    <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden animate-fade-in-up">
      <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
        <div>
          <h3 className="font-bold text-slate-800 text-lg flex items-center gap-2">
            <CornerDownRight className="text-primary"/> مدیریت سریع زیرمجموعه‌ها
          </h3>
          <p className="text-xs text-slate-500 mt-1">
              والد: <strong className="dir-ltr font-mono bg-slate-100 px-1 rounded">{parentSlug}</strong>
          </p>
        </div>
        <button 
          type="button"
          onClick={() => append({ name: '', is_active: true, preview_url: null, banner_box_file: null })} 
          className="btn btn-sm btn-outline btn-primary gap-2"
        >
          <Plus size={16}/> سطر جدید
        </button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="p-6">
        {fields.length === 0 ? (
          <div className="text-center py-10 text-slate-400 border-2 border-dashed border-slate-100 rounded-xl mb-6">
            هنوز زیرمجموعه‌ای اضافه نشده است.
          </div>
        ) : (
          <div className="overflow-x-auto mb-6">
            <table className="table w-full">
              <thead>
                <tr>
                  <th className="w-10">#</th>
                  <th className="w-20">تصویر</th>
                  <th>نام زیردسته</th>
                  <th className="text-center w-24">وضعیت</th>
                  <th className="w-16"></th>
                </tr>
              </thead>
              <tbody>
                {fields.map((field, index) => {
                  // گارد کلاوز برای دسترسی امن به واچ ایندکس فعلی سطر
                  const currentPreview = subsWatch[index]?.preview_url;

                  return (
                  <tr key={field.id} className="hover:bg-slate-50 transition-colors">
                    <td className="text-slate-400 font-mono text-xs">{index + 1}</td>
                    
                    {/* --- بخش آپلود عکس سطر با ساپورت نمایش آدرس سرور و فایل لوکال --- */}
                    <td>
                      <label className="relative flex w-12 h-12 rounded-xl cursor-pointer group bg-slate-100 border border-slate-200 overflow-hidden hover:border-primary transition-all shadow-sm">
                        {currentPreview ? (
                          <img 
                            src={currentPreview} 
                            alt={`preview-${index}`} 
                            className="w-full h-full object-cover" 
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-slate-400 bg-slate-50">
                            <ImageIcon size={20} />
                          </div>
                        )}
                        
                        {/* اورلی شیک هنگام هاور موس */}
                        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity text-white">
                           <Upload size={16} />
                        </div>
                        
                        {/* اینپوت فایل مخفی با آدرس‌دهی داینامیک ایندکس فیلد ارایه */}
                        <input 
                          type="file" 
                          accept="image/*" 
                          className="hidden" 
                          onChange={(e) => handleFileChange(e, index)}
                        />
                      </label>
                    </td>

                    <td>
                      <input 
                        {...register(`subs.${index}.name`, { required: true })}
                        className="input input-sm input-bordered w-full font-bold" 
                        placeholder="نام زیردسته..."
                      />
                    </td>
                    
                    <td className="text-center">
                      <label className="swap swap-rotate text-emerald-600">
                        <input type="checkbox" {...register(`subs.${index}.is_active`)} />
                        <CheckCircle2 size={24} className="swap-on"/>
                        <AlertCircle size={24} className="swap-off text-slate-300"/>
                      </label>
                    </td>

                    <td>
                      <button 
                        type="button" 
                        onClick={() => remove(index)}
                        className="btn btn-xs btn-square btn-ghost text-red-400 hover:bg-red-50"
                        title="حذف از لیست"
                      >
                        <Trash2 size={16}/>
                      </button>
                    </td>
                  </tr>
                )})}
              </tbody>
            </table>
          </div>
        )}

        <div className="flex justify-end pt-4 border-t border-slate-100">
          <button 
            type="submit" 
            disabled={bulkMutation.isPending || (!isDirty && fields.length > 0)}
            className="btn btn-primary px-8 shadow-lg min-w-[150px]"
          >
            {bulkMutation.isPending ? <span className="loading loading-spinner"></span> : <><Save size={18}/> ذخیره لیست</>}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SubCategoryManager;