import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowRight, Save, Loader2, Image as ImageIcon } from 'lucide-react';
import { motion } from 'framer-motion';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import toast from 'react-hot-toast';

import { adminArticleService } from '../../services/adminArticleService';
import { adminBlogCategoryService } from '../../services/adminBlogCategoryService'; // سرویس دسته‌بندی بلاگ که قبلا ساختی
import { articleSchema } from './schemas/articleSchema';
import BlockNoteEditor from './components/BlockNoteEditor';
import ProductMultiSelect from './components/ProductMultiSelect';
import { useAdminArticles } from './hooks/useAdminArticles';
import clsx from 'clsx';

const ArticleEditorPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = !!id;
  
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [categories, setCategories] = useState([]);
  const [previewImage, setPreviewImage] = useState(null);

  const { minimalProducts } = useAdminArticles();

  const { register, handleSubmit, control, reset, formState: { errors } } = useForm({
    resolver: yupResolver(articleSchema),
    defaultValues: { status: 'draft', related_products: [], category: '' }
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // دریافت داینامیک لیست دسته‌بندی‌های بلاگ
        const catsData = await adminBlogCategoryService.getAll();
        // فقط دسته‌های فعال را نشان می‌دهیم
        setCategories(catsData.filter(c => c.is_active));
        
        if (isEditMode) {
          const article = await adminArticleService.getById(id);
          reset({
            title: article.title,
            category: article.category?.toString(),
            summary: article.summary,
            content: article.content,
            meta_title: article.meta_title,
            meta_description: article.meta_description,
            tags: article.tags,
            read_time: article.read_time,
            status: article.status,
            related_products: article.related_products.map(p => p.id || p)
          });
          if (article.image) setPreviewImage(article.image);
        }
      } catch (error) {
        toast.error('خطا در دریافت اطلاعات. اتصال به سرور را بررسی کنید.');
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
        if (key === 'image') {
          // فقط در صورتی فیلد تصویر ارسال می‌شود که کاربر واقعاً فایل جدیدی انتخاب کرده باشد
          if (data.image && data.image.length > 0) {
            formData.append('image', data.image[0]);
          }
        } else if (key === 'related_products') {
           data[key]?.forEach(pId => formData.append('related_products', pId));
        } else if (data[key] !== undefined && data[key] !== null && data[key] !== '') {
          formData.append(key, data[key]);
        }
      });

      if (isEditMode) {
        await adminArticleService.update(id, formData);
        toast.success('مقاله با موفقیت ویرایش شد');
      } else {
        await adminArticleService.create(formData);
        toast.success('مقاله جدید ایجاد شد');
        navigate('/admin/articles');
      }
    } catch (error) {
      toast.error('خطا در ذخیره مقاله');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 relative overflow-hidden">
        <div className="absolute w-[500px] h-[500px] bg-primary/10 rounded-full blur-[100px] animate-pulse"></div>
        <div className="relative z-10 flex flex-col items-center gap-6 bg-white/50 backdrop-blur-xl p-10 rounded-[3rem] shadow-2xl border border-white">
          <Loader2 size={48} className="text-primary animate-spin" />
          <span className="font-black text-xl text-slate-800">در حال دریافت اطلاعات...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f8fafc] pb-32 font-sans selection:bg-primary/20">
      <div className="sticky top-0 z-40 bg-white/70 backdrop-blur-2xl border-b border-white shadow-[0_4px_30px_rgba(0,0,0,0.03)] px-6 py-4 flex justify-between items-center transition-all">
        <div className="flex items-center gap-5">
          <button 
             onClick={() => navigate('/admin/articles')} 
             className="w-10 h-10 flex items-center justify-center bg-white border border-slate-200 text-slate-600 rounded-full shadow-sm hover:bg-slate-50 hover:text-primary transition-all active:scale-95"
          >
            <ArrowRight size={20} />
          </button>
          <div className="flex flex-col">
            <h1 className="text-xl font-black text-slate-800 tracking-tight">
              {isEditMode ? 'ویرایش مقاله' : 'نوشتن مقاله جدید'}
            </h1>
          </div>
        </div>

        <button onClick={handleSubmit(onSubmit)} disabled={isSaving} className="btn btn-primary rounded-full px-8 shadow-lg shadow-primary/30 h-11">
            {isSaving ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
            ذخیره و ثبت
        </button>
      </div>

      <div className="max-w-6xl mx-auto mt-10 px-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <div className="lg:col-span-2 space-y-8">
                <div className="bg-white p-8 rounded-[2rem] shadow-xl shadow-slate-200/30 border border-slate-100">
                    <h2 className="text-lg font-black text-slate-800 mb-6">محتوای اصلی</h2>
                    <div className="space-y-5">
                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">عنوان مقاله *</label>
                            <input type="text" {...register('title')} className={clsx("input input-bordered w-full rounded-xl bg-slate-50 focus:border-primary", errors.title && "border-red-500")} placeholder="مثال: راهنمای جامع چاپ افست" />
                            {errors.title && <p className="text-red-500 text-xs mt-1">{errors.title.message}</p>}
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">خلاصه مقاله</label>
                            <textarea {...register('summary')} className="textarea textarea-bordered w-full rounded-xl bg-slate-50 h-24 resize-none focus:border-primary" placeholder="چکیده کوتاه مقاله..." />
                            {errors.summary && <p className="text-red-500 text-xs mt-1">{errors.summary.message}</p>}
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">متن مقاله *</label>
                            <Controller
                                name="content" control={control}
                                render={({ field }) => <BlockNoteEditor initialHTML={field.value} onChange={field.onChange} />}
                            />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-[2rem] shadow-xl shadow-slate-200/30 border border-slate-100">
                    <h2 className="text-lg font-black text-slate-800 mb-6">سئو و متادیتا</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">Meta Title</label>
                            <input type="text" {...register('meta_title')} className="input input-bordered w-full rounded-xl bg-slate-50" />
                        </div>
                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">کلمات کلیدی (Tags)</label>
                            <input type="text" {...register('tags')} className="input input-bordered w-full rounded-xl bg-slate-50" placeholder="چاپ, افست (با کاما جدا کنید)" />
                        </div>
                        <div className="md:col-span-2">
                            <label className="block text-sm font-bold text-slate-700 mb-2">Meta Description</label>
                            <textarea {...register('meta_description')} className="textarea textarea-bordered w-full rounded-xl bg-slate-50 h-20" />
                        </div>
                    </div>
                </div>
            </div>

            <div className="space-y-8">
                <div className="bg-white p-6 rounded-[2rem] shadow-xl shadow-slate-200/30 border border-slate-100">
                    <h2 className="text-lg font-black text-slate-800 mb-6">تنظیمات انتشار</h2>
                    <div className="space-y-5">
                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">وضعیت مقاله</label>
                            <select {...register('status')} className="select select-bordered w-full rounded-xl bg-slate-50 focus:border-primary">
                                <option value="draft">پیش‌نویس</option>
                                <option value="published">منتشر شده</option>
                                <option value="archived">بایگانی</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">دسته‌بندی *</label>
                            <select {...register('category')} className={clsx("select select-bordered w-full rounded-xl bg-slate-50 focus:border-primary", errors.category && "border-red-500")}>
                                <option value="">انتخاب دسته‌بندی...</option>
                                {categories.map(cat => (
                                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                                ))}
                            </select>
                            {errors.category && <p className="text-red-500 text-xs mt-1">{errors.category.message}</p>}
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">زمان مطالعه (دقیقه)</label>
                            <input type="number" {...register('read_time')} className="input input-bordered w-full rounded-xl bg-slate-50 focus:border-primary" min="1" />
                            {errors.read_time && <p className="text-red-500 text-xs mt-1">{errors.read_time.message}</p>}
                        </div>

                        <div className="relative z-10">
                            <label className="block text-sm font-bold text-slate-700 mb-2">محصولات مرتبط</label>
                            <Controller
                                name="related_products"
                                control={control}
                                render={({ field }) => (
                                    <ProductMultiSelect 
                                        options={minimalProducts} 
                                        value={field.value} 
                                        onChange={field.onChange} 
                                    />
                                )}
                            />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-[2rem] shadow-xl shadow-slate-200/30 border border-slate-100">
                    <h2 className="text-lg font-black text-slate-800 mb-6">تصویر شاخص</h2>
                    <div className="relative group cursor-pointer">
                        <div className="w-full h-48 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 flex items-center justify-center overflow-hidden hover:bg-slate-100 transition-colors">
                            {previewImage ? (
                                <img src={previewImage} alt="Preview" className="w-full h-full object-cover" />
                            ) : (
                                <div className="text-slate-400 flex flex-col items-center gap-2">
                                    <ImageIcon size={32} />
                                    <span className="text-sm font-medium">آپلود تصویر</span>
                                </div>
                            )}
                        </div>
                        <input 
                            type="file" accept="image/*" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            {...register('image')}
                            onChange={(e) => {
                                if(e.target.files?.[0]) setPreviewImage(URL.createObjectURL(e.target.files[0]));
                            }}
                        />
                    </div>
                </div>
            </div>

        </motion.div>
      </div>
    </div>
  );
};

export default ArticleEditorPage;