import React, { useEffect, useState } from 'react';
import { X, AlertCircle, Loader2, Info, Package, PlayCircle } from 'lucide-react';
import ProductCard from '../../../components/product/ProductCard';

// هلپر لینک یوتوب
const getYouTubeEmbedUrl = (url) => {
  if (!url) return null;
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
  const match = url.match(regExp);
  return (match && match[2].length === 11) 
    ? `https://www.youtube.com/embed/${match[2]}?autoplay=1` 
    : null;
};

const TutorialModal = ({ isOpen, onClose, tutorial, isLoading, error }) => {
  const [activeTab, setActiveTab] = useState('details'); // details | products

  // جلوگیری از اسکرول بادی و ریست کردن تب هنگام باز شدن
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      setActiveTab('details');
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => { document.body.style.overflow = 'unset'; };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-900/90 backdrop-blur-sm transition-all duration-300" dir="rtl">
      
      {/* Container اصلی: فیکس شده در وسط صفحه با حداکثر ارتفاع */}
      <div 
        className="bg-white w-full max-w-7xl h-[90vh] rounded-2xl shadow-2xl overflow-hidden flex flex-col lg:flex-row animate-in fade-in zoom-in-95 duration-200 relative"
        onClick={(e) => e.stopPropagation()}
      >
        
        {/* دکمه بستن (شناور برای دسترسی سریع) */}
        <button 
          onClick={onClose}
          className="absolute top-4 left-4 z-50 p-2 bg-black/20 hover:bg-red-500 text-white rounded-full transition-all backdrop-blur-md"
        >
          <X size={20} />
        </button>

        {/* --- بخش ۱: ویدیو پلیر (سمت راست در دسکتاپ - بالا در موبایل) --- */}
        <div className="w-full lg:w-2/3 h-[40vh] lg:h-full bg-black flex items-center justify-center relative group">
          {isLoading ? (
            <div className="text-white flex flex-col items-center gap-3">
              <Loader2 size={40} className="animate-spin text-primary" />
              <span className="text-sm font-light opacity-80">پخشکەر بار دەکرێت</span>
            </div>
          ) : error ? (
            <div className="text-red-400 flex flex-col items-center gap-2">
              <AlertCircle size={40} />
              <span> هەڵە لە بارکردندا</span>
            </div>
          ) : tutorial?.youtube_embed_url ? (
            <iframe
              src={getYouTubeEmbedUrl(tutorial.youtube_embed_url)}
              title={tutorial.title}
              className="w-full h-full border-0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          ) : (
            <div className="flex flex-col items-center text-slate-500">
              <PlayCircle size={64} className="mb-2 opacity-50" />
              <p> ناونیشانی ڤیدیۆ</p>
            </div>
          )}
        </div>

        {/* --- بخش ۲: سایدبار اطلاعات (سمت چپ در دسکتاپ - پایین در موبایل) --- */}
        <div className="w-full lg:w-1/3 h-full flex flex-col bg-slate-50 border-r border-slate-200">
          
          {/* هدر سایدبار */}
          <div className="p-5 border-b border-slate-200 bg-white shrink-0">
            <h3 className="font-bold text-lg text-slate-800 line-clamp-2 leading-tight">
              {tutorial?.title || <span className="animate-pulse bg-slate-200 rounded text-transparent"></span>}
            </h3>
          </div>

          {/* تب‌ها */}
          {tutorial && (
            <div className="flex items-center p-1 bg-slate-100 mx-4 mt-4 rounded-lg shrink-0 select-none">
              <button
                onClick={() => setActiveTab('details')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-md transition-all ${
                  activeTab === 'details' 
                    ? 'bg-white text-primary shadow-sm' 
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <Info size={16} />

              </button>
              <button
                onClick={() => setActiveTab('products')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-md transition-all ${
                  activeTab === 'products' 
                    ? 'bg-white text-primary shadow-sm' 
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <Package size={16} />
                
                {tutorial.related_products?.length > 0 && (
                  <span className="bg-primary/10 text-primary text-[10px] px-1.5 py-0.5 rounded-full">
                    {tutorial.related_products.length}
                  </span>
                )}
              </button>
            </div>
          )}

          {/* محتوای اسکرول‌خور داخلی */}
          <div className="flex-1 overflow-y-auto custom-scrollbar p-5">
            {isLoading ? (
              <div className="space-y-4 mt-4">
                <div className="h-4 bg-slate-200 rounded w-3/4 animate-pulse"></div>
                <div className="h-4 bg-slate-200 rounded w-full animate-pulse"></div>
                <div className="h-4 bg-slate-200 rounded w-5/6 animate-pulse"></div>
              </div>
            ) : (
              <>
                {/* تب توضیحات */}
                {activeTab === 'details' && (
                  <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                    {tutorial?.description ? (
                      <p className="text-slate-600 text-sm leading-7 text-justify whitespace-pre-line">
                        {tutorial.description}
                      </p>
                    ) : (
                      <p className="text-slate-400 text-sm text-center mt-10">هیچ ڕوونکردنەوەیەک بۆ ئەم ڤیدیۆیە تۆمار نەکراوە</p>
                    )}
                  </div>
                )}

                {/* تب محصولات */}
                {activeTab === 'products' && (
                  <div className="animate-in fade-in slide-in-from-bottom-2 duration-300 space-y-4">
                    {tutorial?.related_products?.length > 0 ? (
                      tutorial.related_products.map((rp) => (
                        <div key={rp.id} className="transform transition-transform hover:scale-[1.01]">
                          {/* نسخه فشرده شده ProductCard یا کامپوننت اصلی */}
                          <ProductCard 
                            product={{
                              ...rp, 
                              thumbnail: rp.image, 
                              has_price: false // مخفی کردن قیمت برای تمرکز روی آموزش
                            }} 
                            className="shadow-sm border border-slate-100"
                          />
                        </div>
                      ))
                    ) : (
                      <div className="flex flex-col items-center justify-center text-slate-400 mt-10 gap-2">
                        <Package size={32} className="opacity-50" />
                        <span className="text-sm">هیچ بەرهەمێکی پەیوەندیدار نەدۆزرایەوە</span>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>

          {/* فوتر سایدبار (اختیاری - مثلا دکمه اشتراک گذاری) */}

        </div>

      </div>
    </div>
  );
};

export default TutorialModal;