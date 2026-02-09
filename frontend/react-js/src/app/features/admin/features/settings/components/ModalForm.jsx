// src/app/features/settings/components/ModalForm.jsx
import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { X, Save, ExternalLink } from 'lucide-react';
import { modalSchema } from '../modalSchema'; 
import ImageUploader from '../../categories/components/ImageUploader'; // مسیر را چک کنید

const ModalForm = ({ isOpen, onClose, editData, onSubmit, isSubmitting }) => {
  const { register, handleSubmit, setValue, reset, formState: { errors } } = useForm({
    resolver: zodResolver(modalSchema),
    defaultValues: { is_active: true }
  });

  useEffect(() => {
    if (isOpen) {
      if (editData) {
        reset({
          title: editData.title,
          description: editData.description || '',
          image: editData.image_url,
          cta_text: editData.cta_text || '',
          cta_url: editData.cta_url || '',
          is_active: editData.is_active,
        });
      } else {
        reset({ title: '', description: '', image: null, cta_text: '', cta_url: '', is_active: true });
      }
    }
  }, [isOpen, editData, reset]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl w-full max-w-2xl shadow-2xl border border-slate-100 animate-scale-in my-8">
        
        {/* Header */}
        <div className="flex justify-between items-center p-5 border-b border-slate-100 bg-slate-50/50 rounded-t-3xl">
          <h3 className="font-bold text-lg text-slate-800">
            {editData ? 'ویرایش مودال' : 'ایجاد مودال جدید'}
          </h3>
          <button onClick={onClose} className="btn btn-sm btn-circle btn-ghost text-slate-400 hover:text-red-500">
            <X size={20} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Left Column: Content */}
          <div className="space-y-4">
             <div className="form-control">
                <label className="label font-bold text-sm">عنوان <span className="text-error">*</span></label>
                <input {...register('title')} className={`input input-bordered rounded-xl ${errors.title ? 'input-error' : ''}`} placeholder="مثال: جشنواره تابستانه" />
                {errors.title && <span className="text-error text-xs mt-1">{errors.title.message}</span>}
             </div>

             <div className="form-control">
                <label className="label font-bold text-sm">توضیحات</label>
                <textarea {...register('description')} className="textarea textarea-bordered h-24 rounded-xl" placeholder="متن پیام مودال..."></textarea>
             </div>

             <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-3">
                <div className="text-xs font-bold text-slate-500 mb-2 flex items-center gap-1"><ExternalLink size={12}/> دکمه اقدام (CTA)</div>
                <div className="form-control">
                    <input {...register('cta_text')} className="input input-sm input-bordered rounded-lg" placeholder="متن دکمه (مثلا: خرید کنید)" />
                </div>
                <div className="form-control">
                    <input {...register('cta_url')} className="input input-sm input-bordered rounded-lg dir-ltr" placeholder="https://..." />
                    {errors.cta_url && <span className="text-error text-xs mt-1">{errors.cta_url.message}</span>}
                </div>
             </div>
          </div>

          {/* Right Column: Media & Status */}
          <div className="space-y-6">
             <div className="form-control">
                <label className="label font-bold text-sm">تصویر مودال</label>
                <ImageUploader 
                    defaultImage={editData?.image_url}
                    onChange={(f) => setValue('image', f)}
                    aspectRatio="square" // معمولا مودال‌ها مربعی یا عمودی هستند
                    label="آپلود تصویر"
                />
             </div>

             <div className="form-control bg-white border border-slate-200 p-4 rounded-2xl">
                <label className="label cursor-pointer">
                  <span className="label-text font-bold text-slate-700">وضعیت فعال</span>
                  <input type="checkbox" className="toggle toggle-success" {...register('is_active')} />
                </label>
                <p className="text-[10px] text-slate-400 mt-2 px-1">فقط یک مودال فعال در سایت نمایش داده می‌شود.</p>
             </div>
          </div>

          {/* Footer Actions */}
          <div className="col-span-1 md:col-span-2 pt-4 flex gap-3 border-t border-slate-100 mt-2">
             <button type="button" onClick={onClose} className="btn btn-ghost flex-1 rounded-xl">انصراف</button>
             <button type="submit" disabled={isSubmitting} className="btn btn-primary flex-[2] rounded-xl shadow-lg">
                {isSubmitting ? <span className="loading loading-dots"></span> : <><Save size={18}/> ذخیره تغییرات</>}
             </button>
          </div>

        </form>
      </div>
    </div>
  );
};

export default ModalForm;