// src/app/features/settings/components/SliderModal.jsx
import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { X, Save } from 'lucide-react';
import { sliderSchema } from '../sliderSchema';
// مسیر ImageUploader را بر اساس پروژه خود تنظیم کنید
import ImageUploader from '../../categories/components/ImageUploader'; 

const SliderModal = ({ isOpen, onClose, editData, onSubmit, isSubmitting }) => {
  const { register, handleSubmit, setValue, reset, formState: { errors } } = useForm({
    resolver: zodResolver(sliderSchema),
  });

  useEffect(() => {
    if (isOpen) {
      if (editData) {
        reset({
          name: editData.name,
          image: editData.image_url, // نگاشت image_url به فیلد image
        });
      } else {
        reset({ name: '', image: null });
      }
    }
  }, [isOpen, editData, reset]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-3xl w-full max-w-lg shadow-2xl border border-slate-100 overflow-hidden animate-scale-in">
        
        {/* Header */}
        <div className="flex justify-between items-center p-5 border-b border-slate-100 bg-slate-50/50">
          <h3 className="font-bold text-lg text-slate-800">
            {editData ? 'ویرایش اسلایدر' : 'افزودن اسلایدر جدید'}
          </h3>
          <button onClick={onClose} className="btn btn-sm btn-circle btn-ghost text-slate-400 hover:text-red-500">
            <X size={20} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          
          {/* Name Input */}
          <div className="form-control">
            <label className="label font-bold text-slate-700 text-sm">عنوان اسلایدر</label>
            <input 
              {...register('name')} 
              className={`input input-bordered rounded-xl w-full ${errors.name ? 'input-error' : ''}`}
              placeholder="مثال: تخفیف‌های ویژه نوروز" 
            />
            {errors.name && <span className="text-error text-xs mt-1">{errors.name.message}</span>}
          </div>

          {/* Image Upload */}
          <div>
             <label className="label font-bold text-slate-700 text-sm">تصویر اسلایدر</label>
             <ImageUploader 
                defaultImage={editData?.image_url}
                onChange={(file) => setValue('image', file, { shouldValidate: true })}
                error={errors.image}
                aspectRatio="wide" // برای اسلایدر حالت wide مناسب‌تر است
                label="آپلود تصویر (پیشنهادی: 1920x600)"
             />
             {errors.image && <span className="text-error text-xs mt-1">{errors.image.message}</span>}
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

export default SliderModal;