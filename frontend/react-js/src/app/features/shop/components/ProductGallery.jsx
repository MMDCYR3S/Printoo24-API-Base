// src/app/features/shop/components/ProductGallery.jsx
import { useState, useEffect } from 'react';
import clsx from 'clsx';
import { Image as ImageIcon, Maximize2, Paperclip } from 'lucide-react';
import ProductMediaModal from './ProductMediaModal'; // ایمپورت کامپوننت جدید

const ProductGallery = ({ images = [], attachments = [] }) => {
  const [activeImage, setActiveImage] = useState(null);
  const [activeIndex, setActiveIndex] = useState(0);
  
  // استیت‌های مدیریت مودال
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalInitialTab, setModalInitialTab] = useState('images');

  useEffect(() => {
    if (images.length > 0) {
      setActiveImage(images[0].image_url);
      setActiveIndex(0);
    }
  }, [images]);

  // تابع باز کردن مودال
  const handleOpenModal = (tab = 'images', index = 0) => {
    setModalInitialTab(tab);
    setActiveIndex(index);
    setIsModalOpen(true);
  };

  if (!images || images.length === 0) {
    return (
      <div className="aspect-square bg-slate-50 rounded-3xl border border-slate-100 flex flex-col items-center justify-center text-slate-300">
        <ImageIcon size={48} strokeWidth={1.5} />
        <span className="mt-2 text-sm">تصویر ندارد</span>
      </div>
    );
  }

  return (
    <>
      <div className="flex flex-col gap-4 sticky top-24">
        {/* تصویر اصلی */}
        <div 
          onClick={() => handleOpenModal('images', activeIndex)}
          className="aspect-[4/3] w-full bg-white rounded-3xl border border-slate-100 p-2 shadow-sm overflow-hidden group cursor-zoom-in relative"
        >
          <div className="w-full h-full rounded-2xl overflow-hidden relative bg-slate-50">
             <img 
               src={activeImage} 
               alt="Product Main" 
               className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
             />
             {/* دکمه شناور بزرگنمایی */}
             <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300 flex items-center justify-center">
                <div className="bg-white/90 backdrop-blur-sm text-slate-800 p-3 rounded-full opacity-0 group-hover:opacity-100 scale-75 group-hover:scale-100 transition-all duration-300 shadow-xl">
                  <Maximize2 size={24} />
                </div>
             </div>
          </div>
        </div>

        {/* تصاویر کوچک */}
        <div className="grid grid-cols-4 gap-3">
          {images.map((img, idx) => (
            <button
              key={img.id}
              onClick={() => {
                setActiveImage(img.image_url);
                setActiveIndex(idx);
              }}
              className={clsx(
                "aspect-square rounded-2xl p-1 border-2 transition-all duration-200 bg-white",
                activeImage === img.image_url 
                  ? "border-primary shadow-md scale-95" 
                  : "border-transparent hover:border-slate-200"
              )}
            >
              <img 
                src={img.image_url} 
                alt="Thumb" 
                className="w-full h-full object-cover rounded-xl"
              />
            </button>
          ))}
        </div>

        {/* دکمه پیوست‌ها (فقط در صورت وجود پیوست نمایش داده می‌شود) */}
        {attachments && attachments.length > 0 && (
          <button 
            onClick={() => handleOpenModal('attachments')}
            className="w-full mt-2 flex items-center justify-center gap-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-600 font-bold py-3.5 rounded-2xl transition-all hover:shadow-sm"
          >
            <Paperclip size={18} />
            مشاهده فایل‌های پیوست ({attachments.length})
          </button>
        )}
      </div>

      {/* اتصال کامپوننت مودال */}
      <ProductMediaModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        images={images}
        attachments={attachments}
        initialTab={modalInitialTab}
        initialIndex={activeIndex}
      />
    </>
  );
};

export default ProductGallery;