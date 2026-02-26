import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowRight, Save, Loader2, Image as ImageIcon, Youtube } from 'lucide-react';
import { motion } from 'framer-motion';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import toast from 'react-hot-toast';
import clsx from 'clsx';

import { adminTutorialService } from '../../services/adminTutorialService';
import { tutorialSchema } from './schemas/tutorialSchema';
import { useAdminTutorials } from './hooks/useAdminTutorials';
// حتما مسیر ProductMultiSelect را نسبت به پوشه خودتان تنظیم کنید:
import ProductMultiSelect from '../blog/components/ProductMultiSelect'; 

const TutorialEditorPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = !!id;
  
  const [isLoading, setIsLoading] = useState(isEditMode);
  const [isSaving, setIsSaving] = useState(false);
  const [previewImage, setPreviewImage] = useState(null);

  const { minimalProducts } = useAdminTutorials();

  const { register, handleSubmit, control, reset, watch, formState: { errors } } = useForm({
    resolver: yupResolver(tutorialSchema),
    defaultValues: { is_active: true, related_products: [] }
  });

  const youtubeUrl = watch('youtube_embed_url');

  useEffect(() => {
    const fetchData = async () => {
      if (!isEditMode) return;
      try {
        const tutorial = await adminTutorialService.getById(id);
        reset({
          title: tutorial.title,
          description: tutorial.description,
          youtube_embed_url: tutorial.youtube_embed_url,
          is_active: tutorial.is_active,
          related_products: tutorial.related_products?.map(p => p.id || p) || []
        });
        if (tutorial.thumbnail) setPreviewImage(tutorial.thumbnail);
      } catch (error) {
        toast.error('خطا در دریافت اطلاعات آموزش');
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [id, isEditMode, reset]);

  const onSubmit = async (data) => {
    setIsSaving(true);
    try {
      const formData = new FormData();
      Object.keys(data).forEach(key => {
        if (key === 'thumbnail') {
          // رفع مشکل ارسال عکس: فقط فایل جدید ارسال می‌شود
          const file = data.thumbnail?.[0];
          if (file instanceof File) {
            formData.append('thumbnail', file);
          }
        } else if (key === 'related_products') {
           data[key]?.forEach(pId => formData.append('related_products', pId));
        } else if (data[key] !== undefined && data[key] !== null) {
          formData.append(key, data[key]);
        }
      });

      if (isEditMode) {
        await adminTutorialService.update(id, formData);
        toast.success('آموزش با موفقیت ویرایش شد');
      } else {
        await adminTutorialService.create(formData);
        toast.success('آموزش جدید اضافه شد');
        navigate('/admin/tutorials');
      }
    } catch (error) {
      toast.error('خطا در ذخیره آموزش');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 relative overflow-hidden">
        <Loader2 size={48} className="text-red-500 animate-spin relative z-10" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f8fafc] pb-32 font-sans selection:bg-red-500/20">
      <div className="sticky top-0 z-40 bg-white/70 backdrop-blur-2xl border-b border-white shadow-[0_4px_30px_rgba(0,0,0,0.03)] px-6 py-4 flex justify-between items-center transition-all">
        <div className="flex items-center gap-5">
          <button onClick={() => navigate('/admin/tutorials')} className="w-10 h-10 flex items-center justify-center bg-white border border-slate-200 text-slate-600 rounded-full hover:bg-slate-50 hover:text-red-500 transition-all active:scale-95">
            <ArrowRight size={20} />
          </button>
          <h1 className="text-xl font-black text-slate-800 tracking-tight">
            {isEditMode ? 'ویرایش آموزش ویدیویی' : 'افزودن آموزش جدید'}
          </h1>
        </div>
        <button onClick={handleSubmit(onSubmit)} disabled={isSaving} className="btn btn-error text-white rounded-full px-8 shadow-lg shadow-red-500/30 h-11 border-0">
            {isSaving ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
            ذخیره آموزش
        </button>
      </div>

      <div className="max-w-6xl mx-auto mt-10 px-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <div className="lg:col-span-2 space-y-8">
                <div className="bg-white p-8 rounded-[2rem] shadow-xl shadow-slate-200/30 border border-slate-100">
                    <h2 className="text-lg font-black text-slate-800 mb-6 flex items-center gap-2">
                        <Youtube className="text-red-500" size={24}/> اطلاعات ویدیو
                    </h2>
                    
                    <div className="space-y-5">
                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">عنوان آموزش *</label>
                            <input type="text" {...register('title')} className={clsx("input input-bordered w-full rounded-xl bg-slate-50 focus:border-red-500", errors.title && "border-red-500")} placeholder="مثال: نحوه تنظیم Bleed در ایلاستریتور" />
                            {errors.title && <p className="text-red-500 text-xs mt-1">{errors.title.message}</p>}
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">لینک Embed یوتیوب *</label>
                            <input type="text" dir="ltr" {...register('youtube_embed_url')} className={clsx("input input-bordered w-full rounded-xl bg-slate-50 focus:border-red-500", errors.youtube_embed_url && "border-red-500")} placeholder="https://www.youtube.com/embed/..." />
                            {errors.youtube_embed_url && <p className="text-red-500 text-xs mt-1">{errors.youtube_embed_url.message}</p>}
                        </div>

                        {/* پیش‌نمایش زنده ویدیو یوتیوب */}
                        {youtubeUrl && youtubeUrl.includes('youtube.com/embed/') && !errors.youtube_embed_url && (
                          <div className="mt-4 aspect-video rounded-2xl overflow-hidden border-2 border-slate-100 shadow-inner bg-slate-900">
                            <iframe 
                                width="100%" height="100%" 
                                src={youtubeUrl} 
                                title="YouTube video player" 
                                frameBorder="0" 
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                                allowFullScreen>
                            </iframe>
                          </div>
                        )}

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2 mt-4">توضیحات کوتاه *</label>
                            <textarea {...register('description')} className={clsx("textarea textarea-bordered w-full rounded-xl bg-slate-50 h-32 resize-none focus:border-red-500", errors.description && "border-red-500")} placeholder="درباره این ویدیو توضیح دهید..." />
                            {errors.description && <p className="text-red-500 text-xs mt-1">{errors.description.message}</p>}
                        </div>
                    </div>
                </div>
            </div>

            <div className="space-y-8">
                <div className="bg-white p-6 rounded-[2rem] shadow-xl shadow-slate-200/30 border border-slate-100">
                    <h2 className="text-lg font-black text-slate-800 mb-6">تنظیمات</h2>
                    <div className="space-y-5">
                        <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-100">
                            <span className="text-sm font-bold text-slate-700">وضعیت نمایش</span>
                            <input type="checkbox" {...register('is_active')} className="toggle toggle-success" />
                        </div>

                        <div className="relative z-10">
                            <label className="block text-sm font-bold text-slate-700 mb-2">محصولات مرتبط</label>
                            <Controller
                                name="related_products"
                                control={control}
                                render={({ field }) => (
                                    <ProductMultiSelect options={minimalProducts} value={field.value} onChange={field.onChange} />
                                )}
                            />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-[2rem] shadow-xl shadow-slate-200/30 border border-slate-100">
                    <h2 className="text-lg font-black text-slate-800 mb-6">کاور ویدیو (اختیاری)</h2>
                    <div className="relative group cursor-pointer">
                        <div className="w-full aspect-video rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 flex items-center justify-center overflow-hidden hover:bg-slate-100 transition-colors">
                            {previewImage ? (
                                <img src={previewImage} alt="Preview" className="w-full h-full object-cover" />
                            ) : (
                                <div className="text-slate-400 flex flex-col items-center gap-2">
                                    <ImageIcon size={32} />
                                    <span className="text-sm font-medium">آپلود کاور اختصاصی</span>
                                </div>
                            )}
                        </div>
                        <input 
                            type="file" accept="image/*" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            {...register('thumbnail')}
                            onChange={(e) => {
                                if(e.target.files?.[0]) setPreviewImage(URL.createObjectURL(e.target.files[0]));
                            }}
                        />
                    </div>
                    <p className="text-[10px] text-slate-400 mt-3 text-center">اگر آپلود نکنید، پیش‌نمایش خود یوتیوب نمایش داده می‌شود.</p>
                </div>
            </div>

        </motion.div>
      </div>
    </div>
  );
};

export default TutorialEditorPage;