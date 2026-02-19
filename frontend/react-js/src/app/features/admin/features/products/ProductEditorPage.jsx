// src/app/features/admin/products/ProductEditorPage.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Layers, Settings, Image as ImageIcon, Check, AlertTriangle, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

import { useProductEditor } from './hooks/useProductEditor';
import ProductStep1Form from './components/steps/ProductStep1Form';
import ProductStep2Options from './components/steps/ProductStep2Options';
import ProductStep3Media from './components/steps/ProductStep3Media';

const steps = [
  { id: 'basic', label: 'اطلاعات پایه', icon: Layers },
  { id: 'options', label: 'ویژگی‌ها', icon: Settings },
  { id: 'media', label: 'مدیا و فایل', icon: ImageIcon },
];

const ProductEditorPage = () => {
  const navigate = useNavigate();
  
  const { 
    isEditMode, productId,
    activeTab, setActiveTab, 
    product, isLoading, isError,
    
    saveStep1, isSavingStep1,
    saveStep2, isSavingStep2,
    saveStep3, isSavingStep3,
    
    uploadImageAsync, 
    uploadAttachmentAsync, 
    isUploading 
  } = useProductEditor();

  // --- UI: Loading State ---
  if (isLoading) {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 relative overflow-hidden">
            <div className="absolute w-[500px] h-[500px] bg-primary/10 rounded-full blur-[100px] animate-pulse"></div>
            <div className="relative z-10 flex flex-col items-center gap-6 bg-white/50 backdrop-blur-xl p-10 rounded-[3rem] shadow-2xl shadow-slate-200/50 border border-white">
                <Loader2 size={48} className="text-primary animate-spin" />
                <div className="flex flex-col items-center gap-1">
                    <span className="font-black text-xl text-slate-800">در حال دریافت اطلاعات</span>
                    <span className="text-slate-500 text-sm font-medium">لطفاً چند لحظه صبر کنید...</span>
                </div>
            </div>
        </div>
    );
  }

  // --- UI: Error State ---
  if (isEditMode && isError) {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 relative overflow-hidden">
            <div className="relative z-10 flex flex-col items-center gap-6 bg-white/70 backdrop-blur-xl p-10 rounded-[3rem] shadow-2xl shadow-red-500/10 border border-red-50 text-center max-w-sm">
                <div className="w-24 h-24 bg-red-100 text-red-500 rounded-full flex items-center justify-center shadow-inner">
                    <AlertTriangle size={48}/>
                </div>
                <div className="space-y-2">
                    <h2 className="text-2xl font-black text-slate-800">محصول یافت نشد!</h2>
                    <p className="text-slate-500 text-sm font-medium leading-relaxed">ممکن است محصول حذف شده باشد یا آدرس را اشتباه وارد کرده باشید.</p>
                </div>
                <button 
                   onClick={() => navigate('/admin/products')} 
                   className="btn btn-error text-white rounded-full w-full shadow-lg shadow-red-500/30 hover:scale-[1.02] transition-transform mt-2"
                >
                   بازگشت به لیست محصولات
                </button>
            </div>
        </div>
    );
  }

  // --- UI: Main Content ---
  return (
    <div className="min-h-screen bg-[#f8fafc] pb-32 font-sans selection:bg-primary/20">
      
      {/* Modern Glassmorphic Header */}
      <div className="sticky top-0 z-40 bg-white/70 backdrop-blur-2xl border-b border-white shadow-[0_4px_30px_rgba(0,0,0,0.03)] px-6 py-4 flex justify-between items-center transition-all">
        
        {/* Right Section: Back Button & Title */}
        <div className="flex items-center gap-5">
          <button 
             onClick={() => navigate('/admin/products')} 
             className="w-10 h-10 flex items-center justify-center bg-white border border-slate-200 text-slate-600 rounded-full shadow-sm hover:bg-slate-50 hover:text-primary transition-all active:scale-95"
          >
            <ArrowRight size={20} />
          </button>
          <div className="flex flex-col">
            <h1 className="text-xl font-black text-slate-800 tracking-tight">
              {isEditMode ? `ویرایش: ${product?.shell?.name}` : 'ایجاد محصول جدید'}
            </h1>
            {isEditMode && <span className="text-[11px] text-slate-400 font-bold mt-0.5">شناسه سیستم: {productId}</span>}
          </div>
        </div>

        {/* Center Section: Modern Steps Indicator */}
        <div className="hidden md:flex p-1.5 bg-slate-100/80 backdrop-blur-md rounded-full border border-slate-200/50">
           {steps.map((step, index) => {
             const isActive = step.id === activeTab;
             const canNavigate = isEditMode && product; 
             const isPast = steps.findIndex(s => s.id === activeTab) > index;
             
             return (
               <button
                 key={step.id}
                 onClick={() => canNavigate && setActiveTab(step.id)}
                 disabled={!canNavigate && !isPast && !isActive}
                 className={clsx(
                   "relative flex items-center gap-2 px-6 py-2.5 rounded-full text-sm font-bold transition-all duration-500",
                   isActive 
                      ? "bg-primary text-white shadow-lg shadow-primary/30 scale-100" 
                      : isPast 
                      ? "text-emerald-600 hover:bg-emerald-50/50 cursor-pointer scale-95 hover:scale-100" 
                      : canNavigate 
                      ? "text-slate-500 hover:bg-white cursor-pointer scale-95 hover:scale-100"
                      : "text-slate-400 opacity-40 cursor-not-allowed scale-95"
                 )}
               >
                 {isPast ? <Check size={18} strokeWidth={2.5}/> : <step.icon size={18} strokeWidth={isActive ? 2 : 1.5} />}
                 <span>{step.label}</span>
                 
                 {/* Active Indicator Dot (Optional UX flair) */}
                 {isActive && (
                    <motion.div layoutId="activeTabIndicator" className="absolute inset-0 border-2 border-primary rounded-full z-[-1]"></motion.div>
                 )}
               </button>
             )
           })}
        </div>

        {/* Left Section: Spacer (To keep center aligned) */}
        <div className="w-10 hidden md:block"></div>
      </div>

      {/* Main Form Container */}
      <div className="max-w-6xl mx-auto mt-10 px-6">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20, filter: 'blur(10px)' }}
          animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        >
           {activeTab === 'basic' && (
              <ProductStep1Form 
                 initialData={isEditMode ? product : null} 
                 onSave={saveStep1} 
                 isSaving={isSavingStep1}
                 isEditMode={isEditMode}
              />
           )}

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
                 productId={productId} 
                 
                 // اتصال توابع آپلود مدیا
                 onSave={saveStep3} 
                 onUploadImage={uploadImageAsync}
                 onUploadAttachment={uploadAttachmentAsync}
                 
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