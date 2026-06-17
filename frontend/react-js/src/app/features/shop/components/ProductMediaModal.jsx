// src/app/features/shop/components/ProductMediaModal.jsx
import { useState, useEffect } from 'react';
import { X, ChevronRight, ChevronLeft, Paperclip, Image as ImageIcon, FileText, Film, Download } from 'lucide-react';
import clsx from 'clsx';
import { createPortal } from 'react-dom';

import pageText from '../../../lang/pages.json'

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

  useEffect(() => {
    if (isOpen) {
      setActiveTab(initialTab);
      setCurrentIndex(initialIndex);
      // قفل کردن وحشیانه اسکرول در کل صفحه (افقی و عمودی)
      document.body.style.overflow = 'hidden';
      document.documentElement.style.overflow = 'hidden';
      document.body.style.overflowX = 'hidden';
      document.documentElement.style.overflowX = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
      document.documentElement.style.overflow = 'auto';
      document.body.style.overflowX = 'hidden';
      document.documentElement.style.overflowX = 'hidden';
    }
    
    return () => {
      document.body.style.overflow = 'auto';
      document.documentElement.style.overflow = 'auto';
      document.body.style.overflowX = 'hidden';
      document.documentElement.style.overflowX = 'hidden';
    };
  }, [isOpen, initialTab, initialIndex]);

  if (!isOpen) return null;

  const handleNext = () => setCurrentIndex((prev) => (prev + 1) % images.length);
  const handlePrev = () => setCurrentIndex((prev) => (prev === 0 ? images.length - 1 : prev - 1));

  return createPortal(
    <div 
      // overflow-hidden اضافه شد، انیمیشن زوم حذف شد چون باعث سرریز میشه
      className="fixed inset-0 w-full h-full z-[100] flex items-center justify-center bg-slate-900/80 backdrop-blur-sm p-4 overflow-hidden animate-in fade-in duration-200"
      onClick={onClose} 
    >
      {/* کانتینر محتوای مودال - max-w-[calc(100vw-2rem)] اضافه شد تا دقیقاً تو مانیتور جا بشه */}
      <div 
        className="bg-white w-full max-w-[calc(100vw-2rem)] md:max-w-4xl rounded-[32px] overflow-hidden flex flex-col max-h-[90vh] shadow-2xl"
        onClick={(e) => e.stopPropagation()} 
      >
        
        <div className="flex items-center justify-between p-4 border-b border-slate-100 bg-slate-50/50 overflow-hidden w-full">
          <div className="flex space-x-2 space-x-reverse overflow-hidden max-w-[80%]">
            <button
              onClick={() => setActiveTab('images')}
              className={clsx("btn btn-sm rounded-xl font-bold transition-all whitespace-nowrap", activeTab === 'images' ? "btn-primary shadow-lg shadow-primary/30" : "btn-ghost text-slate-500")}
            >
              <ImageIcon size={18} className="shrink-0" /> 
              <span className="truncate">{pageText.shop.productDetail.productGallery.productMediaModal.images}</span>
            </button>
            {attachments?.length > 0 && (
              <button
                onClick={() => setActiveTab('attachments')}
                className={clsx("btn btn-sm rounded-xl font-bold transition-all whitespace-nowrap", activeTab === 'attachments' ? "btn-primary shadow-lg shadow-primary/30" : "btn-ghost text-slate-500")}
              >
                <Paperclip size={18} className="shrink-0" /> 
                <span className="truncate">{pageText.shop.productDetail.productGallery.productMediaModal.attachments}</span>
              </button>
            )}
          </div>
          <button onClick={onClose} className="btn btn-circle btn-sm btn-ghost hover:bg-red-100 hover:text-red-500 transition-colors shrink-0">
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 bg-slate-50 w-full">
          
          {activeTab === 'images' && (
            <div className="flex flex-col items-center h-full space-y-6 w-full">
              <div className="relative w-full flex-1 min-h-[40vh] md:min-h-[50vh] flex items-center justify-center bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm">
                <img 
                  src={images[currentIndex]?.image_url} 
                  alt="Gallery" 
                  className="max-w-full max-h-[60vh] object-contain transition-opacity duration-300" 
                />
                
                {images.length > 1 && (
                  <>
                    <button onClick={handlePrev} className="absolute right-2 md:right-4 btn btn-circle bg-white/90 hover:bg-white border-none shadow-lg hover:scale-110 transition-transform z-10">
                      <ChevronRight size={24} className="text-slate-800" />
                    </button>
                    <button onClick={handleNext} className="absolute left-2 md:left-4 btn btn-circle bg-white/90 hover:bg-white border-none shadow-lg hover:scale-110 transition-transform z-10">
                      <ChevronLeft size={24} className="text-slate-800" />
                    </button>
                  </>
                )}
              </div>

              <div className="flex gap-3 overflow-x-auto p-2 w-full justify-center scrollbar-hide max-w-full">
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

          {activeTab === 'attachments' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
              {attachments.map((file) => (
                <div key={file.id} className="bg-white p-4 rounded-2xl border border-slate-200 flex items-center gap-4 hover:shadow-lg hover:border-primary/30 transition-all group w-full overflow-hidden">
                  <div className="w-14 h-14 rounded-2xl bg-slate-50 group-hover:bg-primary/5 flex items-center justify-center shrink-0 transition-colors">
                    {getFileIcon(file.file_url)}
                  </div>
                  <div className="flex-1 min-w-0 overflow-hidden">
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
                    className="btn btn-circle btn-ghost text-primary hover:bg-primary/10 shrink-0"
                    title={pageText.shop.productDetail.productGallery.productMediaModal.downloadLook}
                  >
                    <Download size={20} />
                  </a>
                </div>
              ))}
              {attachments.length === 0 && (
                <div className="col-span-full flex flex-col items-center justify-center py-20 text-slate-400 w-full">
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