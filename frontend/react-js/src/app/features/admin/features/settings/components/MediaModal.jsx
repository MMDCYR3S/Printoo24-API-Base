import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { X, Save, Image as ImageIcon, Link as LinkIcon } from 'lucide-react';
import { mediaSchema } from '../mediaSchema';
import ImageUploader from '../../categories/components/ImageUploader'; 

const MediaModal = ({ isOpen, onClose, editData, onSubmit, isSubmitting }) => {
  const { register, handleSubmit, setValue, watch, reset, formState: { errors } } = useForm({
    resolver: zodResolver(mediaSchema),
    defaultValues: { file: null, link: '', is_active: true }
  });

  const isActive = watch('is_active');

  useEffect(() => {
    if (isOpen) {
      if (editData) {
        reset({
          file: editData.file, // در Swagger جدید اسم فیلد عکس file است
          link: editData.link || '',
          is_active: editData.is_active,
        });
      } else {
        reset({ file: null, link: '', is_active: true });
      }
    }
  }, [isOpen, editData, reset]);

  if (!isOpen) return null;

  // تابع واسط برای جلوگیری از ارسال دیتای اضافی به بک‌اند
  const handleFinalSubmit = (data) => {
    // اگر در حالت ایجاد هستیم و عکسی انتخاب نشده، ارور دستی می‌دهیم
    if (!editData && !data.file) {
       alert("انتخاب تصویر برای ایجاد رسانه جدید الزامی است.");
       return;
    }

    const payload = {
      is_active: data.is_active,
      link: data.link
    };

    // فایل جدید فقط در صورتی به سرور ارسال می‌شود که از سیستم انتخاب شده باشد
    if (data.file instanceof File) {
      payload.file = data.file;
    }

    onSubmit(payload);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-3xl w-full max-w-lg shadow-2xl border border-slate-100 overflow-hidden animate-scale-in">
        
        {/* Header */}
        <div className="flex justify-between items-center p-5 border-b border-slate-100 bg-slate-50/50">
          <h3 className="font-bold text-lg text-slate-800 flex items-center gap-2">
            <ImageIcon size={20} className="text-indigo-500" />
            {editData ? 'ویرایش رسانه' : 'آپلود رسانه جدید'}
          </h3>
          <button onClick={onClose} className="btn btn-sm btn-circle btn-ghost text-slate-400 hover:text-red-500">
            <X size={20} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(handleFinalSubmit)} className="p-6 space-y-5">
          
          {/* File Upload Area */}
          <div>
             <label className="label font-bold text-slate-700 text-sm">تصویر بنر (عکس یا گیف)</label>
             <ImageUploader 
                defaultImage={editData?.file} 
                onChange={(file) => setValue('file', file, { shouldValidate: true })}
                error={errors.file}
                aspectRatio="wide" 
                label="آپلود فایل (حداکثر 5 مگابایت)"
             />
             <span className="text-xs text-slate-400 mt-2 block">فرمت‌های مجاز: jpg, png, gif, webp</span>
          </div>

          {/* Link Destination */}
          <div className="form-control">
            <label className="label font-bold text-slate-700 text-sm flex items-center gap-2">
              <LinkIcon size={16} className="text-slate-400"/> لینک مقصد (هنگام کلیک کاربر روی بنر)
            </label>
            <input 
              type="url"
              dir="ltr"
              placeholder="https://example.com/target"
              className={`input input-bordered rounded-xl w-full text-left ${errors.link ? 'input-error' : ''}`}
              {...register('link')}
            />
            {errors.link && <span className="text-error text-xs mt-1">{errors.link.message}</span>}
          </div>

          {/* Status */}
          <div className="form-control bg-slate-50 p-4 rounded-xl border border-slate-100 mt-2">
            <label className="label cursor-pointer justify-start gap-4">
              <input 
                type="checkbox" 
                className="toggle toggle-primary" 
                {...register('is_active')} 
              />
              <div>
                <span className="label-text font-bold text-slate-700 block">وضعیت نمایش</span>
                <span className="text-xs text-slate-400 mt-1 block">
                  {isActive ? 'فعال - سایر رسانه‌ها خودکار غیرفعال می‌شوند' : 'غیرفعال'}
                </span>
              </div>
            </label>
          </div>

          {/* Footer */}
          <div className="pt-4 flex gap-3">
             <button type="button" onClick={onClose} className="btn btn-ghost flex-1 rounded-xl">انصراف</button>
             <button 
                type="submit" 
                disabled={isSubmitting} 
                className="btn btn-primary flex-[2] rounded-xl shadow-lg shadow-primary/20"
             >
                {isSubmitting ? <span className="loading loading-dots"></span> : <><Save size={18}/> ذخیره</>}
             </button>
          </div>

        </form>
      </div>
    </div>
  );
};

export default MediaModal;