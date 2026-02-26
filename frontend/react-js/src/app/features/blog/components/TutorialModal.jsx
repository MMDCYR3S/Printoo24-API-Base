import React, { useEffect } from 'react';
import { X, AlertCircle, Loader2 } from 'lucide-react';
import ProductCard from '../../../components/product/ProductCard';

// هلپر تبدیل لینک به امبد یوتوب (با قابلیت پخش خودکار)
const getYouTubeEmbedUrl = (url) => {
  if (!url) return null;
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
  const match = url.match(regExp);
  if (match && match[2].length === 11) {
    // اضافه کردن autoplay=1 برای شروع خودکار ویدیو
    return `https://www.youtube.com/embed/${match[2]}?autoplay=1`;
  }
  return null;
};

const TutorialModal = ({ isOpen, onClose, tutorial, isLoading, error }) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => { document.body.style.overflow = 'unset'; };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 sm:p-6 lg:p-12" dir="rtl">
      
      <div 
        className="absolute inset-0 bg-slate-900/80 backdrop-blur-md transition-opacity"
        onClick={onClose}
      ></div>

      <div className="relative w-full max-w-5xl max-h-[95vh] bg-white rounded-3xl shadow-2xl flex flex-col animate-in fade-in zoom-in-95 duration-200 overflow-hidden">
        
        <div className="flex items-center justify-between p-4 border-b border-slate-100 bg-white z-10 shrink-0">
          <h3 className="text-lg font-black text-slate-800 line-clamp-1 pr-2">
            {tutorial?.title || 'در حال بارگذاری ویدیو...'}
          </h3>
          <button 
            onClick={onClose}
            className="w-10 h-10 flex items-center justify-center bg-slate-100 hover:bg-red-100 hover:text-red-600 rounded-full text-slate-500 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="overflow-y-auto flex-1 custom-scrollbar">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-32">
              <Loader2 size={48} className="text-primary animate-spin mb-4" />
              <p className="text-slate-500 font-medium">در حال دریافت اطلاعات...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-32 text-red-500">
              <AlertCircle size={48} className="mb-4" />
              <p className="font-medium text-lg">{error}</p>
            </div>
          ) : tutorial ? (
            <div className="pb-10">
              {/* ── استفاده از iframe بومی و بدون باگ ── */}
              <div className="w-full aspect-video bg-black relative">
                {tutorial.youtube_embed_url ? (
                  <iframe
                    src={getYouTubeEmbedUrl(tutorial.youtube_embed_url)}
                    title={tutorial.title}
                    className="absolute top-0 left-0 w-full h-full border-0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  ></iframe>
                ) : (
                  <div className="flex items-center justify-center w-full h-full text-white/50 bg-slate-800 text-lg font-bold">
                    لینک ویدیو یافت نشد!
                  </div>
                )}
              </div>

              <div className="p-6 md:p-10">
                {tutorial.description && (
                  <div className="mb-12">
                    <h4 className="text-xl font-black text-slate-800 mb-4 flex items-center gap-2">
                      توضیحات آموزش
                    </h4>
                    <p className="text-slate-600 leading-[2.2] text-justify font-medium text-[15px] md:text-base">
                      {tutorial.description}
                    </p>
                  </div>
                )}

                {tutorial.related_products && tutorial.related_products.length > 0 && (
                  <div className="mt-8 pt-10 border-t border-slate-100">
                    <h4 className="text-2xl font-black text-slate-800 mb-8 border-r-4 border-primary pr-3">
                      محصولات مرتبط با این آموزش
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                      {tutorial.related_products.map((rp) => {
                        const mappedProduct = {
                          ...rp,
                          thumbnail: rp.image,
                          category: { parent_category: 'معرفی شده در ویدیو' }, 
                          has_price: false 
                        };
                        return (
                          <ProductCard key={rp.id} product={mappedProduct} />
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default TutorialModal;