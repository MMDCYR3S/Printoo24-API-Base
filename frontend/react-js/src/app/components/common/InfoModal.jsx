// src/app/components/common/InfoModal.jsx
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { X, ExternalLink } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { modalService } from '../../services/modalService';

const InfoModal = () => {
  const [isOpen, setIsOpen] = useState(false);

  const { data: modalData } = useQuery({
    queryKey: ['active-modal'],
    queryFn: modalService.getActiveModal,
    staleTime: 1000 * 60 * 15, // کش ۱۵ دقیقه‌ای
    retry: false, // اگر ارور داد (مثلا ۴۰۴ که یعنی مودالی نیست) ریتلای نکن
  });

  useEffect(() => {
    // فقط وقتی دیتا آمد و active بود بررسی کن
    if (modalData?.id && modalData?.is_active) {
      // بررسی کن آیا کاربر قبلاً این مودال خاص (با این ID) را بسته؟
      const seenKey = `seen_modal_${modalData.id}`;
      const hasSeen = localStorage.getItem(seenKey);

      if (!hasSeen) {
        // کمی تأخیر برای حس بهتر (بلافاصله بعد لود صفحه نپره تو صورت کاربر)
        const timer = setTimeout(() => setIsOpen(true), 2000);
        return () => clearTimeout(timer);
      }
    }
  }, [modalData]);

  const handleClose = () => {
    setIsOpen(false);
    if (modalData?.id) {
      // ذخیره در حافظه که این مودال دیده شد
      localStorage.setItem(`seen_modal_${modalData.id}`, 'true');
    }
  };

  if (!isOpen || !modalData) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center px-4">
          {/* Backdrop Blur */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm cursor-pointer"
          />

          {/* Modal Content */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', duration: 0.5 }}
            className="relative w-full max-w-lg bg-white rounded-3xl shadow-2xl overflow-hidden z-10"
          >
            {/* دکمه بستن */}
            <button
              onClick={handleClose}
              className="absolute top-4 right-4 z-20 p-2 bg-black/20 hover:bg-black/40 text-white rounded-full backdrop-blur-md transition-colors"
            >
              <X size={20} />
            </button>

            {/* تصویر مودال */}
            {modalData.image_url && (
              <div className="relative w-full h-48 sm:h-64 bg-slate-100">
                <img
                  src={modalData.image_url}
                  alt={modalData.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-white via-transparent to-transparent h-20 top-auto bottom-0" />
              </div>
            )}

            {/* محتوا */}
            <div className="p-6 sm:p-8 text-center -mt-6 relative z-10">
              <h3 className="text-2xl font-black text-slate-800 mb-3">
                {modalData.title}
              </h3>
              
              <p className="text-slate-500 mb-8 leading-relaxed text-sm sm:text-base">
                {modalData.description}
              </p>

              {/* دکمه اکشن (اگر وجود داشته باشد) */}
              {modalData.cta_text && modalData.cta_url && (
                <a
                  href={modalData.cta_url}
                  target="_blank" // معمولاً لینک‌های تبلیغاتی در تب جدید باز شوند بهتر است
                  rel="noreferrer"
                  onClick={handleClose} // بعد از کلیک مودال بسته شود
                  className="btn btn-primary w-full shadow-lg shadow-primary/30 rounded-xl text-lg font-bold group"
                >
                  {modalData.cta_text}
                  <ExternalLink size={18} className="group-hover:-translate-x-1 transition-transform" />
                </a>
              )}
              
              {/* دکمه بستن متنی (اختیاری) */}
              <button 
                onClick={handleClose}
                className="mt-4 text-xs text-slate-400 hover:text-slate-600 font-medium"
              >
                بستن پنجره
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default InfoModal;