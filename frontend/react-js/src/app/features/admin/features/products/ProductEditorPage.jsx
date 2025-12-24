// src/app/features/admin/products/ProductEditorPage.jsx
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowRight, Layers, Settings, Image as ImageIcon, Save, Check } from 'lucide-react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

// ایمپورت هوک و کامپوننت‌های اصلی
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
  
  // استخراج تمام متدها و استیت‌ها از هوک لاجیک
  const { 
    isEditMode, 
    activeTab, setActiveTab, 
    product, isLoading,
    
    // متدهای مرحله ۱
    saveStep1, isSavingStep1,
    
    // متدهای مرحله ۲ (اضافه شد)
    saveStep2, isSavingStep2,
    
    // متدهای مرحله ۳ (اضافه شد)
    saveStep3, isSavingStep3,
    uploadImage, isUploading
  } = useProductEditor();

  if (isLoading) {
    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50">
            <span className="loading loading-spinner loading-lg text-primary"></span>
        </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50/50 pb-20 font-sans">
      
      {/* === Header (Sticky) === */}
      <div className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200 px-6 py-4 flex justify-between items-center shadow-sm">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/dashboard/products')} className="btn btn-ghost btn-circle btn-sm">
            <ArrowRight size={20} />
          </button>
          <div>
            <h1 className="text-xl font-black text-slate-800">
              {isEditMode ? `ویرایش محصول: ${product?.shell?.name}` : 'ایجاد محصول جدید'}
            </h1>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
               {isEditMode ? 'تغییرات به صورت آنی روی سایت اعمال می‌شود' : 'قدم اول: تعریف هویت محصول'}
            </p>
          </div>
        </div>

        {/* Wizard Steps Indicator */}
        <div className="hidden md:flex gap-1 bg-slate-100 p-1 rounded-xl">
           {steps.map((step, index) => {
             const isActive = step.id === activeTab;
             const isPast = steps.findIndex(s => s.id === activeTab) > index;
             
             return (
               <button
                 key={step.id}
                 onClick={() => isEditMode && setActiveTab(step.id)} // در حالت جدید، کاربر نمی‌تواند بپرد مگر اینکه ذخیره شده باشد
                 disabled={!isEditMode && !isPast && !isActive}
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

        <div className="w-10"></div> {/* Spacer for balance */}
      </div>

      {/* === Main Content Area === */}
      <div className="max-w-5xl mx-auto mt-8 px-6">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
           {/* Step 1: Basic Info */}
           {activeTab === 'basic' && (
              <ProductStep1Form 
                 initialData={product} 
                 onSave={saveStep1} 
                 isSaving={isSavingStep1}
                 isEditMode={isEditMode}
              />
           )}

           {/* Step 2: Options */}
           {activeTab === 'options' && (
              <ProductStep2Options 
                 initialData={product} 
                 onSave={saveStep2} 
                 isSaving={isSavingStep2}
              />
           )}

           {/* Step 3: Media */}
           {activeTab === 'media' && (
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