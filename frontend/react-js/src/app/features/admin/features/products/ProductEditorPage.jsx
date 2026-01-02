// src/app/features/admin/products/ProductEditorPage.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Layers, Settings, Image as ImageIcon, Check, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

import { useProductEditor } from './hooks/useProductEditor';
import ProductStep1Form from './components/steps/ProductStep1Form';
import ProductStep2Options from './components/steps/ProductStep2Options';
import ProductStep3Media from './components/steps/ProductStep3Media';

const steps = [
  { id: 'basic', label: 'اطلاعات پایه و قیمت', icon: Layers },
  { id: 'options', label: 'ویژگی‌ها و آپشن‌ها', icon: Settings },
  { id: 'media', label: 'تصاویر و فایل‌ها', icon: ImageIcon },
];

const ProductEditorPage = () => {
  const navigate = useNavigate();
  
  const { 
    isEditMode, 
    activeTab, setActiveTab, 
    product, isLoading, isError, // ✅ اضافه شدن isError
    
    saveStep1, isSavingStep1,
    saveStep2, isSavingStep2,
    saveStep3, isSavingStep3,
    uploadImage, isUploading
  } = useProductEditor();

  // 1. نمایش لودینگ
  if (isLoading) {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 gap-4">
            <span className="loading loading-spinner loading-lg text-primary"></span>
            <span className="text-slate-400 text-sm animate-pulse">در حال دریافت اطلاعات محصول...</span>
        </div>
    );
  }

  // 2. نمایش خطا (اگر محصول پیدا نشد)
  if (isEditMode && isError) {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 gap-6">
            <div className="p-4 bg-red-50 text-error rounded-full"><AlertTriangle size={48}/></div>
            <h2 className="text-xl font-bold text-slate-800">محصول مورد نظر یافت نشد!</h2>
            <button onClick={() => navigate('/admin/products')} className="btn btn-primary">بازگشت به لیست</button>
        </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50/50 pb-20 font-sans">
      
      {/* === Header === */}
      <div className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200 px-6 py-4 flex justify-between items-center shadow-sm">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/admin/products')} className="btn btn-ghost btn-circle btn-sm">
            <ArrowRight size={20} />
          </button>
          <div>
            <h1 className="text-xl font-black text-slate-800">
              {isEditMode ? `ویرایش محصول: ${product?.shell?.name || '...'}` : 'ایجاد محصول جدید'}
            </h1>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
               {isEditMode ? 'تغییرات به صورت آنی اعمال نمی‌شود (نیاز به ذخیره)' : 'قدم اول: تعریف هویت محصول'}
            </p>
          </div>
        </div>

        {/* Wizard Steps */}
        <div className="hidden md:flex gap-1 bg-slate-100 p-1 rounded-xl">
           {steps.map((step, index) => {
             const isActive = step.id === activeTab;
             // فقط اگر در حالت ادیت باشیم و دیتای محصول موجود باشد می‌توانیم تب عوض کنیم
             const canNavigate = isEditMode && product; 
             const isPast = steps.findIndex(s => s.id === activeTab) > index;
             
             return (
               <button
                 key={step.id}
                 onClick={() => canNavigate && setActiveTab(step.id)}
                 disabled={!canNavigate && !isPast && !isActive}
                 className={clsx(
                   "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-all",
                   isActive ? "bg-white text-primary shadow-sm" : 
                   isPast ? "text-emerald-600 hover:bg-emerald-50" : "text-slate-400 opacity-50 cursor-not-allowed"
                 )}
               >
                 {isPast ? <Check size={16}/> : <step.icon size={16} />}
                 {step.label}
               </button>
             )
           })}
        </div>
        <div className="w-10"></div>
      </div>

      {/* === Main Content === */}
      <div className="max-w-5xl mx-auto mt-8 px-6">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
           {activeTab === 'basic' && (
              <ProductStep1Form 
                 // اگر در حالت ادیت هستیم اما پروداکت هنوز نرسیده (بعید است چون لودینگ هندل شد)، null بفرست
                 initialData={isEditMode ? product : null} 
                 onSave={saveStep1} 
                 isSaving={isSavingStep1}
                 isEditMode={isEditMode}
              />
           )}

           {/* فقط وقتی دیتا داریم اجازه رندر تب‌های بعدی را بده */}
           {activeTab === 'options' && product && (
              <ProductStep2Options 
                 initialData={product} 
                 onSave={saveStep2} 
                 isSaving={isSavingStep2}
              />
           )}

           {activeTab === 'media' && product && (
              <ProductStep3Media 
                 initialData={product} 
                 onSave={saveStep3} 
                 onUpload={uploadImage} 
                 isSaving={isSavingStep3}
                 isUploading={isUploading}
              />
           )}
        </motion.div>
      </div>
    </div>
  );
};

export default ProductEditorPage;