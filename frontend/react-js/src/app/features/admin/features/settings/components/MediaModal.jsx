import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { X, Save, Image as ImageIcon } from 'lucide-react';
import { mediaSchema } from '../mediaSchema';
import ImageUploader from '../../categories/components/ImageUploader'; 

const MediaModal = ({ isOpen, onClose, editData, onSubmit, isSubmitting }) => {
const { register, handleSubmit, setValue, watch, reset, formState: { errors } } = useForm({
    resolver: zodResolver(mediaSchema),
    // تغییر اول: file را حتما اینجا اضافه کنید
    defaultValues: { file: null, is_active: true } 
  });

  const isActive = watch('is_active');

useEffect(() => {
    if (isOpen) {
      if (editData) {
        reset({
          file: editData.file_url,
          is_active: editData.is_active,
        });
      } else {
        // تغییر دوم: مطمئن شویم در حالت ایجاد، فایل null ست می‌شود
        reset({ file: null, is_active: true }); 
      }
    }
  }, [isOpen, editData, reset]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-3xl w-full max-w-lg shadow-2xl border border-slate-100 overflow-hidden animate-scale-in">
        
        {/* Header */}
        <div className="flex justify-between items-center p-5 border-b border-slate-100 bg-slate-50/50">
          <h3 className="font-bold text-lg text-slate-800 flex items-center gap-2">
            <ImageIcon size={20} className="text-indigo-500" />
            {editData ? 'ویرایش رسانه نوار بالا' : 'افزودن رسانه جدید'}
          </h3>
          <button onClick={onClose} className="btn btn-sm btn-circle btn-ghost text-slate-400 hover:text-red-500">
            <X size={20} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          
          {/* File Upload */}
          <div>
             <label className="label font-bold text-slate-700 text-sm">فایل رسانه (بنر نوار بالا)</label>
             <ImageUploader 
                defaultImage={editData?.file_url}
                onChange={(file) => setValue('file', file, { shouldValidate: true })}
                error={errors.file}
                aspectRatio="wide" 
                label="آپلود فایل (مناسب برای نوار بالای سایت)"
             />
             {errors.file && <span className="text-error text-xs mt-1 block">{errors.file.message}</span>}
          </div>

          {/* Is Active Toggle */}
          <div className="form-control bg-slate-50 p-4 rounded-xl border border-slate-100">
            <label className="label cursor-pointer justify-start gap-4">
              <input 
                type="checkbox" 
                className="toggle toggle-primary" 
                {...register('is_active')} 
              />
              <div>
                <span className="label-text font-bold text-slate-700 block">وضعیت نمایش</span>
                <span className="text-xs text-slate-400 mt-1 block">
                  {isActive ? 'این رسانه در سایت نمایش داده می‌شود' : 'این رسانه مخفی شده است'}
                </span>
              </div>
            </label>
          </div>

          {/* Footer Actions */}
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