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
  
  // رفرنس برای ذخیره URL های پیش‌نمایش جهت پاکسازی از مموری مرورگر (Best Practice)
  const previewUrls = useRef([]);

  const { control, register, handleSubmit, reset, setValue, watch, formState: { isDirty } } = useForm({
    defaultValues: { subs: [] }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "subs"
  });

  // دریافت مقادیر لحظه‌ای برای نمایش پیش‌نمایش عکس‌ها
  const subsWatch = watch("subs");

  useEffect(() => {
    if (parentCategory?.children) {
      const formattedData = parentCategory.children.map(child => ({
        id: child.id,
        name: child.name,
        is_active: child.is_active ?? true,
        // گرفتن عکس قبلی از سرور (در صورت وجود)
        preview_url: child.banners?.box || null, 
        banner_box_file: null // فایل جدید باینری
      }));
      reset({ subs: formattedData });
    }

    // Cleanup function: جلوگیری از Memory Leak برای عکس‌های آپلود شده
    return () => {
      previewUrls.current.forEach(url => URL.revokeObjectURL(url));
    };
  }, [parentCategory, reset]);

  // هندل کردن انتخاب فایل
  const handleFileChange = (e, index) => {
    const file = e.target.files[0];
    if (file) {
      // 1. ذخیره فایل باینری در State فرم
      setValue(`subs.${index}.banner_box_file`, file, { shouldDirty: true });
      
      // 2. ساخت URL پیش‌نمایش لوکال
      const objectUrl = URL.createObjectURL(file);
      previewUrls.current.push(objectUrl);
      setValue(`subs.${index}.preview_url`, objectUrl);
    }
  };

  const bulkMutation = useMutation({
    mutationFn: (data) => {
      // ✅ ساخت FormData بجای JSON خالص
      const formData = new FormData();

      data.subs.forEach((item, index) => {
        // ⚠️ مهم: نحوه نام‌گذاری کلیدها در آرایه FormData به بک‌اند شما بستگی دارد.
        // متداول‌ترین حالت برای دریافت آرایه در بک‌اند فرمت زیر است: `[0]name` یا `0[name]`
        // اگر بک‌اند شما ارور داد، این بخش (الگوی استرینگ) را طبق نیاز بک‌اند تغییر دهید.
        const prefix = `[${index}]`;

        formData.append(`${prefix}name`, item.name);
        formData.append(`${prefix}is_active`, item.is_active);
        formData.append(`${prefix}parent_slug`, parentSlug);

        if (item.id) {
          formData.append(`${prefix}id`, item.id);
        }

        // اگر فایل جدیدی انتخاب شده، آن را ضمیمه کن
        if (item.banner_box_file) {
          formData.append(`${prefix}banner_box`, item.banner_box_file);
        }
      });

      return adminCategoryService.bulkUpsert(formData);
    },
    onSuccess: () => {
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
                  <th className="w-16">تصویر</th>
                  <th>نام زیردسته</th>
                  <th className="text-center w-24">وضعیت</th>
                  <th className="w-16"></th>
                </tr>
              </thead>
              <tbody>
                {fields.map((field, index) => {
                  const currentPreview = subsWatch[index]?.preview_url;

                  return (
                  <tr key={field.id} className="hover:bg-slate-50 transition-colors">
                    <td className="text-slate-400 font-mono text-xs">{index + 1}</td>
                    
                    {/* --- بخش آپلود عکس UI --- */}
                    <td>
                      <label className="relative flex w-10 h-10 rounded-lg cursor-pointer group bg-slate-100 border border-slate-200 overflow-hidden hover:border-primary transition-all">
                        {currentPreview ? (
                          <img src={currentPreview} alt="preview" className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-slate-400">
                            <ImageIcon size={18} />
                          </div>
                        )}
                        {/* Overlay زمان Hover */}
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity text-white">
                           <Upload size={14} />
                        </div>
                        {/* اینپوت مخفی */}
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