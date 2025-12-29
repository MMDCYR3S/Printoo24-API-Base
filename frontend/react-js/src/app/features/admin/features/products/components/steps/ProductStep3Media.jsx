// src/app/features/admin/products/components/steps/ProductStep3Media.jsx
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Reorder, AnimatePresence, motion } from 'framer-motion';
import { 
  Image as ImageIcon, UploadCloud, X, Star, 
  Film, FileText, Link as LinkIcon, Trash2, 
  GripVertical, PlayCircle, CheckCircle2, AlertCircle 
} from 'lucide-react';
import clsx from 'clsx';
import toast from 'react-hot-toast';

const ProductStep3Media = ({ initialData, onSave, onUpload, isSaving }) => {
  
  // --- States ---
  
  // 1. Images (Reorderable)
  const [images, setImages] = useState(initialData?.images || []);
  
  // 2. Attachments (Videos & Docs)
  // فرض: اتچمنت‌های قبلی را داریم. ما باید لیست جدید و حذفی‌ها را مدیریت کنیم.
  const [attachments, setAttachments] = useState(initialData?.attachments || []);
  
  // لیست‌هایی برای API Sync
  const [idsToLink, setIdsToLink] = useState([]); // فایل‌های جدید آپلود شده
  const [idsToUnlink, setIdsToUnlink] = useState([]); // فایل‌های حذف شده از سرور
  
  // وضعیت آپلود
  const [uploadingState, setUploadingState] = useState({ 
     type: null, // 'image' | 'video' | 'doc'
     progress: 0 
  });

  // --- Handlers: Images ---

  const onDropImages = useCallback(async (acceptedFiles) => {
    if (!acceptedFiles?.length) return;

    setUploadingState({ type: 'image', progress: 10 });
    const toastId = toast.loading('در حال آپلود تصاویر...');

    try {
      // آپلود موازی تصاویر
      const uploadPromises = acceptedFiles.map(file => {
         const formData = new FormData();
         formData.append('image', file);
         // فراخوانی متد آپلود تصویر از هوک پدر
         return onUpload(formData, 'image'); 
      });

      const uploadedImages = await Promise.all(uploadPromises);
      
      // اضافه کردن به لیست نمایش (تصاویر نیاز به Link ندارند، خودشان در پروداکت ست می‌شوند معمولا)
      // اما اگر API شما جداست، منطق را چک کنید. معمولا Image Upload مستقیم وصل میکند.
      // طبق API شما: image_orders میخواهد، پس یعنی تصاویر قبلا وصل شدند.
      
      setImages(prev => [...prev, ...uploadedImages]);
      toast.success('تصاویر بارگذاری شدند', { id: toastId });

    } catch (error) {
      console.error(error);
      toast.error('خطا در آپلود تصاویر', { id: toastId });
    } finally {
      setUploadingState({ type: null, progress: 0 });
    }
  }, [onUpload]);

  const removeImage = (index, imgId) => {
    // حذف از UI
    const newImages = [...images];
    newImages.splice(index, 1);
    setImages(newImages);
    
    // اگر نیاز به Unlink برای تصاویر هم هست، اینجا اضافه شود. 
    // اما معمولا تصاویر با image_orders مدیریت میشوند.
  };

  // --- Handlers: Attachments (Video/Doc) ---

  const handleAttachmentUpload = async (e, type) => {
    const files = e.target.files;
    if (!files?.length) return;

    setUploadingState({ type, progress: 20 });
    const toastId = toast.loading(`در حال آپلود ${type === 'video' ? 'ویدیو' : 'فایل'}...`);

    try {
        const formData = new FormData();
        // نام فیلد بسته به API شما (مثلا 'file' یا 'attachment')
        formData.append('file', files[0]); 
        formData.append('type', type); // متادیتای نوع فایل

        // فراخوانی متد آپلود جنرال
        const result = await onUpload(formData, 'attachment');
        
        // افزودن به لیست UI
        const newAtt = {
            id: result.id,
            file: result.file || URL.createObjectURL(files[0]), // نمایش موقت یا لینک سرور
            type: type, // 'video' or 'doc'
            name: files[0].name
        };

        setAttachments(prev => [...prev, newAtt]);
        
        // افزودن به لیست Link برای ارسال نهایی
        setIdsToLink(prev => [...prev, result.id]);
        
        toast.success('فایل ضمیمه شد', { id: toastId });

    } catch (error) {
        toast.error('آپلود ناموفق بود', { id: toastId });
    } finally {
        setUploadingState({ type: null, progress: 0 });
    }
  };

  const removeAttachment = (id) => {
      // حذف از UI
      setAttachments(prev => prev.filter(a => a.id !== id));
      
      // اگر فایل جدید بود (در Link هست)، از Link حذف کن
      if (idsToLink.includes(id)) {
          setIdsToLink(prev => prev.filter(i => i !== id));
      } else {
          // اگر فایل قدیمی بود، به Unlink اضافه کن
          setIdsToUnlink(prev => [...prev, id]);
      }
  };

  // --- Final Save ---
  const handleFinalSave = () => {
    const payload = {
        // 1. لیست تصاویر به ترتیب جدید
        image_orders: images.map(img => img.id),
        
        // 2. فایل‌های جدید برای اتصال
        attachment_ids_to_link: idsToLink,
        
        // 3. فایل‌های قدیمی برای حذف اتصال
        attachment_ids_to_unlink: idsToUnlink
    };

    onSave(payload);
  };

  // --- Dropzone Config ---
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: onDropImages,
    accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.webp'] },
    multiple: true
  });

  return (
    <div className="max-w-6xl mx-auto pb-32 space-y-8">
       
       {/* === SECTION 1: PRODUCT GALLERY (Priority) === */}
       <div className="card bg-white shadow-xl shadow-slate-200/50 border border-slate-100 p-6 rounded-[2rem]">
          <div className="flex items-center gap-3 mb-6">
             <div className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl">
                <ImageIcon size={24} strokeWidth={1.5}/>
             </div>
             <div>
                <h3 className="font-bold text-lg text-slate-800">گالری تصاویر محصول</h3>
                <p className="text-xs text-slate-500">تصویر اول به عنوان <strong className="text-indigo-600">کاور اصلی</strong> نمایش داده می‌شود. (برای تغییر ترتیب، بکشید و رها کنید)</p>
             </div>
          </div>

          {/* Upload Area */}
          <div 
             {...getRootProps()} 
             className={clsx(
                "border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer mb-8",
                isDragActive ? "border-indigo-500 bg-indigo-50" : "border-slate-200 hover:border-indigo-300 hover:bg-slate-50",
                uploadingState.type === 'image' && "opacity-50 pointer-events-none"
             )}
          >
             <input {...getInputProps()} />
             <div className="flex flex-col items-center gap-3 text-slate-400">
                <div className="w-16 h-16 bg-white rounded-full shadow-sm flex items-center justify-center mb-2">
                    {uploadingState.type === 'image' ? <span className="loading loading-spinner text-indigo-600"></span> : <UploadCloud size={32} className="text-indigo-500"/>}
                </div>
                <p className="text-sm font-bold text-slate-600">تصاویر را اینجا رها کنید یا کلیک کنید</p>
                <p className="text-[10px] opacity-70">JPG, PNG, WEBP (Max 2MB)</p>
             </div>
          </div>

          {/* Images Grid (Reorderable) */}
          <Reorder.Group axis="y" values={images} onReorder={setImages} className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
             {images.map((img, index) => (
                <Reorder.Item key={img.id} value={img} className="relative aspect-square cursor-grab active:cursor-grabbing group">
                    <motion.div layoutId={`img-${img.id}`} className="w-full h-full rounded-2xl overflow-hidden border border-slate-100 shadow-sm relative bg-white">
                        <img src={img.image || img.url} alt="Product" className="w-full h-full object-cover"/>
                        
                        {/* Overlay Actions */}
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 backdrop-blur-[2px]">
                            <button 
                               onClick={() => removeImage(index, img.id)}
                               className="btn btn-sm btn-circle btn-error text-white shadow-lg"
                               title="حذف تصویر"
                            >
                               <Trash2 size={16}/>
                            </button>
                        </div>

                        {/* Badges */}
                        <div className="absolute top-2 right-2 pointer-events-none">
                            {index === 0 ? (
                                <span className="badge badge-warning gap-1 text-[10px] font-bold shadow-sm">
                                   <Star size={10} fill="currentColor"/> کاور
                                </span>
                            ) : (
                                <span className="badge badge-ghost bg-white/80 backdrop-blur text-[10px] font-mono shadow-sm">
                                   #{index + 1}
                                </span>
                            )}
                        </div>
                    </motion.div>
                </Reorder.Item>
             ))}
          </Reorder.Group>
          
          {images.length === 0 && (
              <div className="text-center py-10 text-slate-300 italic text-xs">
                 هنوز تصویری آپلود نشده است.
              </div>
          )}
       </div>

       {/* === SECTION 2: VIDEOS & ATTACHMENTS === */}
       <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
           
           {/* Videos Manager */}
           <div className="card bg-white shadow-xl shadow-slate-200/50 border border-slate-100 p-6 rounded-[2rem]">
               <div className="flex justify-between items-start mb-6">
                   <div className="flex items-center gap-3">
                       <div className="p-3 bg-rose-50 text-rose-600 rounded-2xl"><Film size={24}/></div>
                       <div>
                          <h3 className="font-bold text-lg text-slate-800">ویدیوهای محصول</h3>
                          <p className="text-xs text-slate-500">معرفی، آنباکس یا آموزش استفاده</p>
                       </div>
                   </div>
                   
                   {/* Upload Buttons */}
                   <div className="flex gap-2">
                       <input 
                          type="file" id="video-upload" className="hidden" accept="video/*"
                          onChange={(e) => handleAttachmentUpload(e, 'video')}
                       />
                       <label htmlFor="video-upload" className="btn btn-sm btn-outline btn-error gap-2 rounded-xl">
                           {uploadingState.type === 'video' ? <span className="loading loading-spinner loading-xs"></span> : <UploadCloud size={16}/>}
                           آپلود فایل
                       </label>
                       {/* لینک فعلا غیرفعال تا اندپوینت مشخص شود */}
                       <button className="btn btn-sm btn-ghost text-slate-400 gap-2 rounded-xl" onClick={() => toast('قابلیت لینک بزودی اضافه می‌شود', { icon: '🚧' })}>
                           <LinkIcon size={16}/> لینک
                       </button>
                   </div>
               </div>

               <div className="space-y-3 max-h-[300px] overflow-y-auto custom-scrollbar pr-1">
                   {attachments.filter(a => a.type === 'video' || a.file?.includes('.mp4')).map((vid) => (
                       <div key={vid.id} className="flex items-center gap-3 p-3 bg-slate-50 border border-slate-100 rounded-2xl group">
                           <div className="w-12 h-12 bg-rose-100 text-rose-500 rounded-xl flex items-center justify-center shrink-0">
                               <PlayCircle size={24}/>
                           </div>
                           <div className="flex-1 min-w-0">
                               <h5 className="font-bold text-xs text-slate-700 truncate">{vid.name || 'ویدیوی بی‌نام'}</h5>
                               <span className="text-[10px] text-slate-400">ID: {vid.id}</span>
                           </div>
                           <div className="flex gap-1">
                               <button className="cursor-grab btn btn-xs btn-square btn-ghost text-slate-300"><GripVertical size={14}/></button>
                               <button onClick={() => removeAttachment(vid.id)} className="btn btn-xs btn-square btn-ghost text-error"><Trash2 size={14}/></button>
                           </div>
                       </div>
                   ))}
                   {attachments.filter(a => a.type === 'video').length === 0 && (
                       <div className="text-center py-8 border-2 border-dashed border-slate-100 rounded-2xl text-slate-400 text-xs">
                           ویدیویی وجود ندارد
                       </div>
                   )}
               </div>
           </div>

           {/* Documents Manager */}
           <div className="card bg-white shadow-xl shadow-slate-200/50 border border-slate-100 p-6 rounded-[2rem]">
               <div className="flex justify-between items-start mb-6">
                   <div className="flex items-center gap-3">
                       <div className="p-3 bg-emerald-50 text-emerald-600 rounded-2xl"><FileText size={24}/></div>
                       <div>
                          <h3 className="font-bold text-lg text-slate-800">مستندات و فایل‌ها</h3>
                          <p className="text-xs text-slate-500">کاتالوگ، قالب طراحی، راهنما (PDF/Zip)</p>
                       </div>
                   </div>
                   
                   <div>
                       <input 
                          type="file" id="doc-upload" className="hidden" accept=".pdf,.zip,.rar,.doc,.docx"
                          onChange={(e) => handleAttachmentUpload(e, 'doc')}
                       />
                       <label htmlFor="doc-upload" className="btn btn-sm btn-outline btn-success gap-2 rounded-xl">
                           {uploadingState.type === 'doc' ? <span className="loading loading-spinner loading-xs"></span> : <UploadCloud size={16}/>}
                           آپلود فایل
                       </label>
                   </div>
               </div>

               <div className="space-y-3 max-h-[300px] overflow-y-auto custom-scrollbar pr-1">
                   {attachments.filter(a => a.type === 'doc' || (!a.type && !a.file?.includes('.mp4'))).map((doc) => (
                       <div key={doc.id} className="flex items-center gap-3 p-3 bg-slate-50 border border-slate-100 rounded-2xl">
                           <div className="w-10 h-10 bg-emerald-100 text-emerald-600 rounded-xl flex items-center justify-center shrink-0">
                               <FileText size={20}/>
                           </div>
                           <div className="flex-1 min-w-0">
                               <h5 className="font-bold text-xs text-slate-700 truncate">{doc.name || 'فایل ضمیمه'}</h5>
                               <span className="text-[10px] text-slate-400 font-mono dir-ltr">{doc.file?.split('.').pop()?.toUpperCase()}</span>
                           </div>
                           <button onClick={() => removeAttachment(doc.id)} className="btn btn-xs btn-square btn-ghost text-error"><Trash2 size={14}/></button>
                       </div>
                   ))}
                   {attachments.filter(a => a.type === 'doc').length === 0 && (
                       <div className="text-center py-8 border-2 border-dashed border-slate-100 rounded-2xl text-slate-400 text-xs">
                           فایلی آپلود نشده است
                       </div>
                   )}
               </div>
           </div>
       </div>

       {/* === FOOTER ACTION === */}
       <div className="fixed bottom-6 left-6 z-50">
           <button 
              onClick={handleFinalSave}
              disabled={isSaving || uploadingState.type !== null}
              className="btn btn-primary h-14 px-10 rounded-full shadow-2xl shadow-primary/40 text-lg font-bold hover:scale-105 active:scale-95 transition-all"
           >
              {isSaving ? <span className="loading loading-spinner"></span> : <CheckCircle2 size={22}/>}
              انتشار نهایی محصول
           </button>
       </div>

    </div>
  );
};

export default ProductStep3Media;