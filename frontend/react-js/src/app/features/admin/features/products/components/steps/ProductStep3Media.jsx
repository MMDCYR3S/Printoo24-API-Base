// src/app/features/admin/products/components/steps/ProductStep3Media.jsx
import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Image as ImageIcon, UploadCloud, Star, 
  Film, FileText, Trash2, PlayCircle, CheckCircle2, 
  Loader2, ArrowRight, ArrowLeft 
} from 'lucide-react';
import clsx from 'clsx';
import toast from 'react-hot-toast';

// تابع کمکی آدرس‌دهی
const getImageUrl = (img) => {
    if (img.preview) return img.preview;
    if (img.image?.startsWith('http')) return img.image;
    const BASE_API_URL = 'http://localhost:9010'; 
    return `${BASE_API_URL}${img.image}`;
};

const ProductStep3Media = ({ 
    initialData, 
    onSave, 
    onUploadImage, 
    onUploadAttachment, 
    isSaving 
}) => {
  
  // --- States ---
  const [images, setImages] = useState([]);
  const [attachments, setAttachments] = useState(initialData?.attachments || []);
  
  const [idsToLink, setIdsToLink] = useState([]); 
  const [idsToUnlink, setIdsToUnlink] = useState([]); 
  const [uploadingState, setUploadingState] = useState({ type: null, progress: 0 });

  // Init
  useEffect(() => {
      if (initialData?.images && images.length === 0) {
          setImages(initialData.images.map(img => ({
              ...img,
              uniqueId: img.id || `server-${Math.random()}`
          })));
      }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialData]);

  // --- 1. هندلر تصاویر (Optimistic UI) ---
  const onDropImages = useCallback(async (acceptedFiles) => {
    if (!acceptedFiles?.length) return;
    if (!onUploadImage) return toast.error("خطا در توابع آپلود");

    setUploadingState({ type: 'image', progress: 10 });
    const toastId = toast.loading('در حال پردازش...');

    const newOptimisticImages = acceptedFiles.map(file => ({
        file: file,
        preview: URL.createObjectURL(file),
        uniqueId: `temp-${Math.random()}`,
        isUploading: true,
        id: null
    }));

    // افزودن به ته لیست
    setImages(prev => [...prev, ...newOptimisticImages]);

    try {
      for (const optImg of newOptimisticImages) {
         const formData = new FormData();
         formData.append('image', optImg.file);
         
         const result = await onUploadImage(formData);
         
         setImages(prev => prev.map(img => {
             if (img.uniqueId === optImg.uniqueId) {
                 return {
                     ...img,
                     id: result.id,
                     image: result.image, 
                     isUploading: false,
                 };
             }
             return img;
         }));
      }
      toast.success('آپلود انجام شد', { id: toastId });
    } catch (error) {
      console.error(error);
      toast.error('خطا در آپلود', { id: toastId });
      setImages(prev => prev.filter(img => !img.isUploading));
    } finally {
      setUploadingState({ type: null, progress: 0 });
    }
  }, [onUploadImage]);

  // --- Logic جدید جابجایی (بدون درگ) ---
  const moveImage = (index, direction) => {
    const newImages = [...images];
    if (direction === 'prev' && index > 0) {
        // جابجایی با قبلی (سمت راست در RTL)
        [newImages[index], newImages[index - 1]] = [newImages[index - 1], newImages[index]];
    } else if (direction === 'next' && index < newImages.length - 1) {
        // جابجایی با بعدی (سمت چپ در RTL)
        [newImages[index], newImages[index + 1]] = [newImages[index + 1], newImages[index]];
    }
    setImages(newImages);
  };

  const removeImage = (uniqueId) => {
    setImages(prev => prev.filter(img => img.uniqueId !== uniqueId));
  };

  // --- 2. هندلر فایل‌ها (Attachments) ---
  const handleAttachmentUpload = async (e, type) => {
    const files = e.target.files;
    if (!files?.length) return;
    if (!onUploadAttachment) return toast.error("خطا در توابع آپلود");

    setUploadingState({ type, progress: 20 });
    const toastId = toast.loading('آپلود فایل...');

    try {
        const formData = new FormData();
        formData.append('file', files[0]);
        formData.append('name', files[0].name);

        const result = await onUploadAttachment(formData);
        
        const newAtt = {
            id: result.id,
            file: result.file,
            type: type,
            name: files[0].name
        };

        setAttachments(prev => [...prev, newAtt]);
        setIdsToLink(prev => [...prev, result.id]);
        toast.success('فایل ضمیمه شد', { id: toastId });
    } catch (error) {
        toast.error('آپلود ناموفق بود', { id: toastId });
    } finally {
        setUploadingState({ type: null, progress: 0 });
        e.target.value = '';
    }
  };

  const removeAttachment = (id) => {
      setAttachments(prev => prev.filter(a => a.id !== id));
      if (idsToLink.includes(id)) {
          setIdsToLink(prev => prev.filter(i => i !== id));
      } else {
          setIdsToUnlink(prev => [...prev, id]);
      }
  };

  // --- 3. ذخیره نهایی ---
  const handleFinalSave = () => {
    const validImages = images.filter(img => img.id);
    if (validImages.length !== images.length) {
        return toast.error("صبر کنید تا آپلود تمام شود");
    }

    const payload = {
        image_orders: validImages.map(img => img.id),
        attachment_ids_to_link: idsToLink,
        attachment_ids_to_unlink: idsToUnlink
    };
    onSave(payload);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: onDropImages,
    accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.webp'] },
    multiple: true
  });

  return (
    <div className="max-w-6xl mx-auto pb-32 space-y-8 animate-fade-in-up">
       
       {/* === SECTION 1: IMAGES === */}
       <div className="card bg-white shadow-xl shadow-slate-200/50 border border-slate-100 p-6 rounded-[2rem]">
          <div className="flex items-center gap-3 mb-6">
             <div className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl"><ImageIcon size={24}/></div>
             <div>
                <h3 className="font-bold text-lg text-slate-800">گالری تصاویر</h3>
                <p className="text-xs text-slate-500">برای تغییر ترتیب، از <strong className="text-indigo-600">فلش‌های روی عکس</strong> استفاده کنید.</p>
             </div>
          </div>

          <div {...getRootProps()} className={clsx("border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer mb-8 transition-colors", isDragActive ? "border-indigo-500 bg-indigo-50" : "border-slate-200 hover:bg-slate-50")}>
             <input {...getInputProps()} />
             <div className="flex flex-col items-center gap-3 text-slate-400">
                {uploadingState.type === 'image' ? <span className="loading loading-spinner text-indigo-600"></span> : <UploadCloud size={32}/>}
                <p className="text-sm font-bold">تصاویر را اینجا رها کنید</p>
             </div>
          </div>

          {/* GRID (No Reorder, Just Map) */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
             <AnimatePresence>
             {images.map((img, index) => (
                <motion.div 
                    layout
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.5 }}
                    key={img.uniqueId} 
                    className="relative aspect-square group"
                >
                    <div className={clsx("w-full h-full rounded-2xl overflow-hidden border shadow-sm relative bg-white transition-all", img.isUploading && "opacity-80 border-indigo-300")}>
                        <img 
                            src={getImageUrl(img)} 
                            alt="" 
                            className="w-full h-full object-cover" 
                            onError={(e) => {e.target.src='/placeholder.png'}}
                        />
                        
                        {/* Loading Overlay */}
                        {img.isUploading && (
                            <div className="absolute inset-0 bg-white/60 flex items-center justify-center"><Loader2 size={24} className="animate-spin text-indigo-600"/></div>
                        )}

                        {/* Controls Overlay (Always visible on touch, hover on desktop) */}
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2">
                            
                            {/* Move Buttons */}
                            <div className="flex items-center gap-2">
                                {index > 0 && (
                                    <button 
                                        type="button"
                                        onClick={() => moveImage(index, 'prev')}
                                        className="btn btn-xs btn-circle btn-ghost bg-white/20 text-white hover:bg-white hover:text-indigo-600"
                                        title="جلو (راست)"
                                    >
                                        <ArrowRight size={14}/>
                                    </button>
                                )}
                                
                                <button 
                                    type="button"
                                    onClick={() => removeImage(img.uniqueId)}
                                    className="btn btn-sm btn-circle btn-error text-white shadow-lg"
                                    title="حذف"
                                >
                                   <Trash2 size={16}/>
                                </button>

                                {index < images.length - 1 && (
                                    <button 
                                        type="button"
                                        onClick={() => moveImage(index, 'next')}
                                        className="btn btn-xs btn-circle btn-ghost bg-white/20 text-white hover:bg-white hover:text-indigo-600"
                                        title="عقب (چپ)"
                                    >
                                        <ArrowLeft size={14}/>
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Badges */}
                        <div className="absolute top-2 right-2 pointer-events-none z-10">
                            {index === 0 ? (
                                <span className="badge badge-warning gap-1 text-[10px] font-bold shadow-md ring-1 ring-white">
                                   <Star size={10} fill="currentColor"/> کاور
                                </span>
                            ) : (
                                <span className="badge badge-ghost bg-white/90 backdrop-blur text-[10px] font-mono shadow-sm">
                                   #{index + 1}
                                </span>
                            )}
                        </div>
                    </div>
                </motion.div>
             ))}
             </AnimatePresence>
          </div>
          
          {images.length === 0 && (
              <div className="text-center py-10 text-slate-300 italic text-xs">
                 هنوز تصویری اضافه نشده است.
              </div>
          )}
       </div>

       {/* === SECTION 2: ATTACHMENTS === */}
       <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
           <div className="card bg-white shadow-xl border border-slate-100 p-6 rounded-[2rem]">
               <div className="flex justify-between items-center mb-6">
                   <h3 className="font-bold text-lg text-slate-800 flex items-center gap-2"><Film className="text-rose-500"/> ویدیوها</h3>
                   <div>
                       <input type="file" id="video-upload" className="hidden" accept="video/*" onChange={(e) => handleAttachmentUpload(e, 'video')} />
                       <label htmlFor="video-upload" className="btn btn-sm btn-outline btn-error gap-2 rounded-xl cursor-pointer">آپلود</label>
                   </div>
               </div>
               <div className="space-y-3">
                   {attachments.filter(a => a.type === 'video' || a.file?.includes('.mp4')).map((vid) => (
                       <div key={vid.id} className="flex items-center gap-3 p-3 bg-slate-50 border border-slate-100 rounded-2xl">
                           <PlayCircle size={20} className="text-rose-500"/>
                           <span className="flex-1 text-xs truncate">{vid.name}</span>
                           <button onClick={() => removeAttachment(vid.id)} className="btn btn-xs btn-square btn-ghost text-error"><Trash2 size={14}/></button>
                       </div>
                   ))}
               </div>
           </div>
           
           <div className="card bg-white shadow-xl border border-slate-100 p-6 rounded-[2rem]">
               <div className="flex justify-between items-center mb-6">
                   <h3 className="font-bold text-lg text-slate-800 flex items-center gap-2"><FileText className="text-emerald-500"/> فایل‌ها</h3>
                   <div>
                       <input type="file" id="doc-upload" className="hidden" accept=".pdf,.zip,.rar" onChange={(e) => handleAttachmentUpload(e, 'doc')} />
                       <label htmlFor="doc-upload" className="btn btn-sm btn-outline btn-success gap-2 rounded-xl cursor-pointer">آپلود</label>
                   </div>
               </div>
               <div className="space-y-3">
                   {attachments.filter(a => a.type === 'doc' || (!a.type && !a.file?.includes('.mp4'))).map((doc) => (
                       <div key={doc.id} className="flex items-center gap-3 p-3 bg-slate-50 border border-slate-100 rounded-2xl">
                           <FileText size={20} className="text-emerald-500"/>
                           <span className="flex-1 text-xs truncate">{doc.name}</span>
                           <button onClick={() => removeAttachment(doc.id)} className="btn btn-xs btn-square btn-ghost text-error"><Trash2 size={14}/></button>
                       </div>
                   ))}
               </div>
           </div>
       </div>

       {/* Footer */}
       <div className="fixed bottom-6 left-6 z-50">
           <button onClick={handleFinalSave} disabled={isSaving || uploadingState.type !== null} className="btn btn-primary h-14 px-10 rounded-full shadow-2xl text-lg font-bold">
              {isSaving ? <span className="loading loading-spinner"></span> : <CheckCircle2 size={22}/>}
              انتشار نهایی محصول
           </button>
       </div>
    </div>
  );
};

export default ProductStep3Media;