// src/app/features/shop/components/ProductMediaModal.jsx
import { useState, useEffect } from 'react';
import { X, ChevronRight, ChevronLeft, Paperclip, Image as ImageIcon, FileText, Film, Download } from 'lucide-react';
import clsx from 'clsx';
import { createPortal } from 'react-dom';

import pageText from '../../../lang/pages.json'

// یک تابع کمکی برای تشخیص نوع فایل از روی فرمت آن و نمایش آیکون مناسب
const getFileIcon = (url) => {
  if (!url) return <FileText size={24} />;
  const extension = url.split('.').pop().toLowerCase();
  if (['mp4', 'webm', 'ogg'].includes(extension)) return <Film size={24} className="text-purple-500" />;
  if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension)) return <ImageIcon size={24} className="text-blue-500" />;
  return <FileText size={24} className="text-orange-500" />;
};

const ProductMediaModal = ({ 
  isOpen, 
  onClose, 
  images = [], 
  attachments = [], 
  initialTab = 'images', 
  initialIndex = 0 
}) => {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [currentIndex, setCurrentIndex] = useState(initialIndex);

  // ریست کردن استیت مودال هر بار که باز می‌شود
  useEffect(() => {
    if (isOpen) {
      setActiveTab(initialTab);
      setCurrentIndex(initialIndex);
      // جلوگیری از اسکرول صفحه اصلی وقتی مودال باز است
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, initialTab, initialIndex]);

  if (!isOpen) return null;

  const handleNext = () => setCurrentIndex((prev) => (prev + 1) % images.length);
  const handlePrev = () => setCurrentIndex((prev) => (prev === 0 ? images.length - 1 : prev - 1));

  return createPortal(
    // پس‌زمینه (Backdrop) - کلیک روی اینجا باعث بسته شدن می‌شود
    <div 
      className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/80 backdrop-blur-sm p-4 animate-in fade-in zoom-in-95 duration-200"
      onClick={onClose} // <--- این خط اضافه شد
    >
      {/* کانتینر محتوای مودال - کلیک روی اینجا باعث بسته نشدن می‌شود */}
      <div 
        className="bg-white w-full max-w-4xl rounded-[32px] overflow-hidden flex flex-col max-h-[90vh] shadow-2xl"
        onClick={(e) => e.stopPropagation()} // <--- این خط جلوی انتقال کلیک به بیرون را می‌گیرد
      >
        
        {/* هدر مودال */}
        <div className="flex items-center justify-between p-4 border-b border-slate-100 bg-slate-50/50">
          <div className="flex space-x-2 space-x-reverse">
            <button
              onClick={() => setActiveTab('images')}
              className={clsx("btn btn-sm rounded-xl font-bold transition-all", activeTab === 'images' ? "btn-primary shadow-lg shadow-primary/30" : "btn-ghost text-slate-500")}
            >
              <ImageIcon size={18} /> {pageText.shop.productDetail.productGallery.productMediaModal.images}
            </button>
            {attachments?.length > 0 && (
              <button
                onClick={() => setActiveTab('attachments')}
                className={clsx("btn btn-sm rounded-xl font-bold transition-all", activeTab === 'attachments' ? "btn-primary shadow-lg shadow-primary/30" : "btn-ghost text-slate-500")}
              >
                <Paperclip size={18} /> {pageText.shop.productDetail.productGallery.productMediaModal.attachments} ({attachments.length})
              </button>
            )}
          </div>
          <button onClick={onClose} className="btn btn-circle btn-sm btn-ghost hover:bg-red-100 hover:text-red-500 transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* محتوای مودال */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 bg-slate-50">
          
          {/* تب تصاویر */}
          {activeTab === 'images' && (
            <div className="flex flex-col items-center h-full space-y-6">
              {/* پس‌زمینه عکس سفید شد (bg-white اضافه شد) */}
              <div className="relative w-full flex-1 min-h-[40vh] md:min-h-[50vh] flex items-center justify-center bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm">
                <img 
                  src={images[currentIndex]?.image_url} 
                  alt="Gallery" 
                  className="max-w-full max-h-[60vh] object-contain transition-opacity duration-300" 
                />
                
                {images.length > 1 && (
                  <>
                    <button onClick={handlePrev} className="absolute right-4 btn btn-circle bg-white/90 hover:bg-white border-none shadow-lg hover:scale-110 transition-transform">
                      <ChevronRight size={24} className="text-slate-800" />
                    </button>
                    <button onClick={handleNext} className="absolute left-4 btn btn-circle bg-white/90 hover:bg-white border-none shadow-lg hover:scale-110 transition-transform">
                      <ChevronLeft size={24} className="text-slate-800" />
                    </button>
                  </>
                )}
              </div>

              {/* تامبنیل‌ها در مودال */}
              <div className="flex gap-3 overflow-x-auto p-2 w-full justify-center scrollbar-hide">
                {images.map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => setCurrentIndex(idx)}
                    className={clsx(
                      "w-16 h-16 md:w-20 md:h-20 rounded-2xl overflow-hidden border-2 flex-shrink-0 transition-all duration-300",
                      currentIndex === idx ? "border-primary scale-110 shadow-md" : "border-transparent opacity-60 hover:opacity-100"
                    )}
                  >
                    <img src={img.image_url} alt={`thumb-${idx}`} className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* تب پیوست‌ها */}
          {activeTab === 'attachments' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {attachments.map((file) => (
                <div key={file.id} className="bg-white p-4 rounded-2xl border border-slate-200 flex items-center gap-4 hover:shadow-lg hover:border-primary/30 transition-all group">
                  <div className="w-14 h-14 rounded-2xl bg-slate-50 group-hover:bg-primary/5 flex items-center justify-center shrink-0 transition-colors">
                    {getFileIcon(file.file_url)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-bold text-sm text-slate-800 truncate" dir="ltr" title={file.name}>
                      {file.name}
                    </h4>
                    <span className="text-xs text-slate-400 mt-1 block">
                      {new Date(file.created_at).toLocaleDateString('EN')}
                    </span>
                  </div>
                  <a 
                    href={file.file_url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="btn btn-circle btn-ghost text-primary hover:bg-primary/10"
                    title={pageText.shop.productDetail.productGallery.productMediaModal.downloadLook}
                  >
                    <Download size={20} />
                  </a>
                </div>
              ))}
              {attachments.length === 0 && (
                <div className="col-span-full flex flex-col items-center justify-center py-20 text-slate-400">
                  <Paperclip size={48} className="opacity-20 mb-4" />
                  <p>{pageText.shop.productDetail.productGallery.productMediaModal.attachmentsNotFound}</p>
                </div>
              )}
            </div>
          )}
        </div>

      </div>

    </div> , document.body
  );
};

export default ProductMediaModal;