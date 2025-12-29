// src/app/features/admin/products/components/steps/ProductStep3Media.jsx
import React, { useState, useEffect } from 'react';
import { 
  UploadCloud, Image as ImageIcon, X, Star, 
  ArrowLeft, ArrowRight, FileText, Download , CheckCircle2
} from 'lucide-react';
import clsx from 'clsx';
import { motion } from 'framer-motion';

const ProductStep3Media = ({ initialData, onSave, onUpload, isSaving, isUploading }) => {
  // مدیریت لوکال تصاویر برای نمایش آنی
  const [images, setImages] = useState(initialData?.images || []);
  const [attachments, setAttachments] = useState(initialData?.attachments || []); // اگر فایل ضمیمه دارید

  // --- Image Upload Handler ---
  const handleImageUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    // آپلود تک تک فایل‌ها
    for (let i = 0; i < files.length; i++) {
       const formData = new FormData();
       formData.append('image', files[i]);
       
       try {
         // فراخوانی متد آپلود که از والد پاس داده شده
         const uploadedImage = await onUpload(formData);
         setImages(prev => [...prev, uploadedImage]);
       } catch (error) {
         console.error("Upload failed", error);
       }
    }
  };

  // --- Reorder Logic ---
  const moveImage = (index, direction) => {
    const newImages = [...images];
    if (direction === 'left' && index > 0) {
       [newImages[index], newImages[index - 1]] = [newImages[index - 1], newImages[index]];
    } else if (direction === 'right' && index < newImages.length - 1) {
       [newImages[index], newImages[index + 1]] = [newImages[index + 1], newImages[index]];
    }
    setImages(newImages);
  };

  const removeImage = (id) => {
    if(confirm('آیا از حذف این تصویر مطمئن هستید؟')) {
       setImages(prev => prev.filter(img => img.id !== id));
       // نکته: در بک‌اند هم باید هندل شود یا در زمان Save نهایی لیست جدید فرستاده شود
    }
  };

  // --- Save Handler ---
  const handleFinalSave = () => {
    const payload = {
      // فقط لیست ID ها به ترتیب ارسال می‌شود
      image_orders: images.map(img => img.id),
      // اگر فایل ضمیمه داشتید:
      attachment_ids_to_link: attachments.map(a => a.id)
    };
    onSave(payload);
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4">
       
       {/* --- Upload Area --- */}
       <div className="bg-white p-8 rounded-3xl border-2 border-dashed border-slate-200 text-center hover:border-primary/50 hover:bg-slate-50 transition-colors relative group">
          <input 
             type="file" 
             multiple 
             accept="image/*" 
             onChange={handleImageUpload}
             className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
             disabled={isUploading}
          />
          <div className="flex flex-col items-center justify-center gap-4">
             <div className="p-4 bg-primary/10 text-primary rounded-full group-hover:scale-110 transition-transform">
                {isUploading ? <span className="loading loading-spinner"></span> : <UploadCloud size={32}/>}
             </div>
             <div>
                <h3 className="text-lg font-bold text-slate-700">تصاویر محصول را اینجا رها کنید</h3>
                <p className="text-slate-400 text-sm mt-1">یا کلیک کنید تا فایل‌ها انتخاب شوند (JPG, PNG)</p>
             </div>
          </div>
       </div>

       {/* --- Gallery Grid --- */}
       <div>
          <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
             <ImageIcon size={20}/> گالری تصاویر ({images.length})
          </h3>
          
          {images.length === 0 ? (
             <div className="text-center py-10 text-slate-400 text-sm bg-slate-50 rounded-2xl">
                هنوز تصویری آپلود نشده است.
             </div>
          ) : (
             <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {images.map((img, index) => (
                   <motion.div 
                      layout
                      key={img.id}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="group relative aspect-square bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
                   >
                      <img src={img.image} alt="Product" className="w-full h-full object-cover" />
                      
                      {/* Overlay Actions */}
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-between p-2">
                         <div className="flex justify-end">
                            <button onClick={() => removeImage(img.id)} className="btn btn-xs btn-circle btn-error text-white">
                               <X size={14}/>
                            </button>
                         </div>
                         
                         {/* Order Controls */}
                         <div className="flex justify-between items-center gap-1">
                            {index > 0 && (
                               <button onClick={() => moveImage(index, 'left')} className="btn btn-xs btn-square btn-ghost text-white hover:bg-white/20">
                                  <ArrowRight size={16}/> {/* راست به معنی قبلی در RTL */}
                               </button>
                            )}
                            {index === 0 && (
                               <span className="badge badge-warning badge-sm gap-1 text-xs">
                                  <Star size={10} fill="currentColor"/> اصلی
                               </span>
                            )}
                            {index < images.length - 1 && (
                               <button onClick={() => moveImage(index, 'right')} className="btn btn-xs btn-square btn-ghost text-white hover:bg-white/20 ml-auto">
                                  <ArrowLeft size={16}/>
                               </button>
                            )}
                         </div>
                      </div>
                   </motion.div>
                ))}
             </div>
          )}
       </div>

       {/* --- Final Action --- */}
       <div className="flex justify-end pt-6 border-t border-slate-200">
          <button 
             onClick={handleFinalSave}
             disabled={isSaving || isUploading}
             className="btn btn-primary px-10 h-12 rounded-xl text-lg shadow-xl shadow-primary/20"
          >
             {isSaving ? <span className="loading loading-spinner"></span> : <CheckCircle2 size={20}/>}
             پایان و انتشار محصول
          </button>
       </div>
    </div>
  );
};

export default ProductStep3Media;