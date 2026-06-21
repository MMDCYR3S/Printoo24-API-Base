// src/app/components/common/HomePageModal.jsx
import { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { homeService } from '../../services/homeService';

/**
 * مودال اطلاع‌رسانی صفحه اصلی
 *
 * رفتار:
 * - هنگام mount شدن، مودال فعال را از سرور می‌گیرد.
 * - اگر سرور null یا آبجکت خالی برگرداند → هیچ چیزی رندر نمی‌شود.
 * - اگر مودال فعال باشد:
 *     • یک‌بار در هر نشست (session) نمایش داده می‌شود.
 *     • کلید sessionStorage بر اساس id مودال ذخیره می‌شود؛
 *       بنابراین اگر ادمین مودال را عوض کند، دوباره به کاربر نمایش داده می‌شود.
 * - بستن با: دکمه ×، کلیک روی اورلی، یا کلید Escape.
 *
 * نکته: اگر خواستی هر بار صفحه رفرش شد نمایش داده شود،
 *       فقط خط مربوط به sessionStorage را پاک کن.
 */
const STORAGE_PREFIX = 'home_modal_seen_';

const HomePageModal = () => {
  const [modal, setModal] = useState(null);
  const [isOpen, setIsOpen] = useState(false);

  // ── دریافت مودال فعال ──
  useEffect(() => {
    let isMounted = true;

    (async () => {
      try {
        const data = await homeService.getActiveModal();

        // اگر null یا آبجکت خالی بود → کاری نکن
        if (!data || (typeof data === 'object' && Object.keys(data).length === 0)) {
          return;
        }
        // حداقل یک فیلد معتبر باید داشته باشد (image_url یا title)
        if (!data.image_url && !data.title) {
          return;
        }

        if (!isMounted) return;

        // چک کردن نشست: آیا این مودال قبلاً دیده شده؟
        const seenKey = `${STORAGE_PREFIX}${data.id}`;
        const alreadySeen = sessionStorage.getItem(seenKey) === '1';

        setModal(data);

        if (!alreadySeen) {
          // یک تأخیر کوچک تا صفحه اول لود شود، بعد مودال بیاید
          const timer = setTimeout(() => setIsOpen(true), 600);
          // ثبت در نشست (حتی قبل از بستن، تا در حین لود دوباره باز نشود)
          sessionStorage.setItem(seenKey, '1');
          return () => clearTimeout(timer);
        }
      } catch (err) {
        // بی‌صدا لاگ کن تا تجربه کاربر خراب نشود
        console.warn('بارگذاری مودال صفحه اصلی ناموفق بود:', err);
      }
    })();

    return () => {
      isMounted = false;
    };
  }, []);

  // ── بستن مودال ──
  const handleClose = useCallback(() => {
    setIsOpen(false);
  }, []);

  // ─ـ کلید Escape برای بستن ──
  useEffect(() => {
    if (!isOpen) return;

    const onKey = (e) => {
      if (e.key === 'Escape') handleClose();
    };
    window.addEventListener('keydown', onKey);
    // قفل اسکرول بدنه هنگام باز بودن مودال
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      window.removeEventListener('keydown', onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [isOpen, handleClose]);

  // ── اگر مودالی نیست → هیچی ──
  if (!modal) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.25 }}
          className="fixed inset-0 z-[100] flex items-center justify-center p-4"
          onClick={handleClose} // ← کلیک روی اورلی → بستن
        >
          {/* اورلی */}
          <div className="absolute inset-0 bg-black/55 backdrop-blur-[3px]" />

          {/* ── پنل مودال ── */}
          <motion.div
            initial={{ opacity: 0, scale: 0.92, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 8 }}
            transition={{ type: 'spring', stiffness: 260, damping: 24 }}
            onClick={(e) => e.stopPropagation()} // ← کلیک داخل پنل → بسته نشود
            className="
              relative z-10
              w-full max-w-lg
              bg-white
              rounded-2xl overflow-hidden
              shadow-2xl shadow-black/30
              flex flex-col
              max-h-[90vh]
            "
          >
            {/* ── دکمه بستن ── */}
            <button
              type="button"
              onClick={handleClose}
              aria-label="close"
              className="
                absolute top-3 left-3 z-20
                w-9 h-9 rounded-full
                bg-white/85 backdrop-blur
                flex items-center justify-center
                text-slate-600 hover:text-red-500
                hover:bg-white
                shadow-md
                transition-all duration-200
                active:scale-90
              "
            >
              <X size={18} strokeWidth={2.4} />
            </button>

            <div className="flex flex-col overflow-y-auto custom-scrollbar">
              {/* ── تصویر ── */}
              {modal.image_url && (
                <div className="relative w-full bg-slate-50">
                  <img
                    src={modal.image_url}
                    alt={modal.title || 'home modal'}
                    className="block w-full h-auto max-h-[55vh] object-cover"
                    draggable={false}
                  />
                </div>
              )}

              {/* ── محتوای متنی ── */}
              <div className="p-5 md:p-6 flex flex-col gap-3 text-right">
                {modal.title && (
                  <h2 className="text-lg md:text-xl font-extrabold text-slate-800 leading-snug">
                    {modal.title}
                  </h2>
                )}

                {modal.description && (
                  <p className="text-sm md:text-[15px] text-slate-500 leading-[1.85] font-medium whitespace-pre-line">
                    {modal.description}
                  </p>
                )}

                {/* ── دکمه CTA ── */}
                {modal.cta_text && modal.cta_url && (
                  <a
                    href={modal.cta_url}
                    target="_blank"
                    rel="noreferrer"
                    onClick={handleClose}
                    className="
                      mt-2
                      inline-flex items-center justify-center
                      px-5 py-3 rounded-xl
                      bg-gradient-to-l from-primary to-primary/90
                      text-white text-sm font-bold
                      shadow-md shadow-primary/20
                      hover:shadow-lg hover:shadow-primary/30
                      active:scale-[0.98]
                      transition-all duration-200
                    "
                  >
                    {modal.cta_text}
                  </a>
                )}
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default HomePageModal;
