// src/app/features/layout/topMediaService.jsx
import { useEffect, useState } from 'react';
import { topMediaService } from '../../services/topMediaService';

/**
 * نوار رسانه بالای هدر
 * - عرض تمام صفحه (w-full)
 * - ارتفاع بر اساس نسبت طبیعی تصویر (h-auto) → ثابت نیست
 * - فقط در صورتی نمایش داده می‌شود که عکس فعالی از سمت سرور بیاید
 * - در صورت خطا یا نبود رسانه، هیچ چیزی رندر نمی‌شود (null)
 */
const TopMedia = () => {
  const [media, setMedia] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    (async () => {
      try {
        const data = await topMediaService.getActiveMedia();
        // فقط اگر فیلد is_active فعال بود و file_url موجود بود نمایش بده
        if (isMounted && data && data.is_active && data.file_url) {
          setMedia(data);
        }
      } catch (err) {
        // خطا را بی‌صدا لاگ می‌کنیم تا تجربه کاربر خراب نشود
        console.warn('بارگذاری رسانه بالای هدر ناموفق بود:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    })();

    return () => {
      isMounted = false;
    };
  }, []);

  // در حال لود یا بدون رسانه فعال → چیزی نمایش نده
  if (loading || !media) return null;

  return (
    <div className="w-full block bg-white">
      <img
        src={media.file_url}
        alt="top media"
        // w-full → عرض تمام صفحه
        // h-auto → ارتفاع بر اساس نسبت طبیعی عکس (ثابت نیست)
        // block → حذف فاصله پایین تصویر (inline gap)
        className="block w-full h-auto"
        draggable={false}
      />
    </div>
  );
};

export default TopMedia;
