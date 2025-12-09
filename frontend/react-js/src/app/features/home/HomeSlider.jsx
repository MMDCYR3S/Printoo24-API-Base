// src/app/features/home/HomeSlider.jsx
import { useQuery } from '@tanstack/react-query';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Autoplay, Pagination, Navigation, EffectFade } from 'swiper/modules';
import { Image as ImageIcon } from 'lucide-react';

// استایل‌های اجباری سوایپر
import 'swiper/css';
import 'swiper/css/pagination';
import 'swiper/css/navigation';
import 'swiper/css/effect-fade';

import { homeService } from '../../services/homeService';

const HomeSlider = () => {
  const { data: sliders, isLoading, error } = useQuery({
    queryKey: ['home-sliders'],
    queryFn: homeService.getSliders,
    staleTime: 1000 * 60 * 60, // کش کردن دیتا برای ۱ ساعت (چون اسلایدر دیر به دیر عوض میشه)
  });

  // 1. حالت لودینگ: نمایش اسکلتون زیبا
  if (isLoading) {
    return (
      <div className="w-full h-[200px] md:h-[400px] bg-slate-100 rounded-2xl animate-pulse flex items-center justify-center text-slate-300">
        <ImageIcon size={48} />
      </div>
    );
  }

  // 2. اگر دیتایی نبود یا ارور داشت، چیزی نشان نده (یا می‌تونیم یه بنر پیش‌فرض بذاریم)
  if (error || !sliders || sliders.length === 0) {
    return null; 
  }

  return (
    <section className="relative group">
      <Swiper
        modules={[Autoplay, Pagination, Navigation, EffectFade]}
        spaceBetween={0}
        slidesPerView={1}
        effect={'fade'} // افکت محو شدن برای زیبایی بیشتر در دسکتاپ
        speed={1000} // سرعت انیمیشن
        loop={true}
        autoplay={{
          delay: 5000,
          disableOnInteraction: false,
        }}
        pagination={{
          clickable: true,
          dynamicBullets: true,
        }}
        navigation={true} // دکمه‌های چپ و راست (در CSS می‌تونیم کاستوم کنیم)
        className="w-full h-auto rounded-2xl overflow-hidden shadow-lg"
      >
        {sliders.map((slide) => (
          <SwiperSlide key={slide.id}>
            <div className="relative w-full aspect-[16/9] md:aspect-[3/1] bg-slate-800">
              {/* تصویر اسلایدر */}
              <img
                src={slide.image_url}
                alt={slide.name}
                className="w-full h-full object-cover"
                loading="lazy"
              />
              
              {/* لایه گرادینت برای خوانایی متن (اگر متنی باشد) */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent pointer-events-none"></div>

              {/* کپشن یا متن اسلایدر (اختیاری) */}
              {slide.name && (
                <div className="absolute bottom-8 right-8 md:bottom-12 md:right-16 text-white max-w-2xl animate-in fade-in slide-in-from-bottom-4 duration-700">
                  <h2 className="text-xl md:text-3xl font-black drop-shadow-md mb-2">
                    {slide.name}
                  </h2>
                </div>
              )}
            </div>
          </SwiperSlide>
        ))}
      </Swiper>
      
      {/* استایل‌دهی دکمه‌های نویگیشن سوایپر برای هماهنگی با تم */}
      <style jsx global>{`
        .swiper-button-next, .swiper-button-prev {
          color: white;
          background: rgba(0,0,0,0.3);
          width: 40px;
          height: 40px;
          border-radius: 50%;
          backdrop-filter: blur(4px);
        }
        .swiper-button-next:after, .swiper-button-prev:after {
          font-size: 18px;
          font-weight: bold;
        }
        .swiper-pagination-bullet-active {
          background-color: var(--color-primary) !important;
        }
      `}</style>
    </section>
  );
};

export default HomeSlider;