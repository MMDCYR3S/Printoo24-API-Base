// src/app/features/home/HomeSlider.jsx
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Autoplay, Pagination, EffectFade } from 'swiper/modules'; 
import { Image as ImageIcon, ChevronRight, ChevronLeft } from 'lucide-react'; 

// استایل‌های اجباری سوایپر
import 'swiper/css';
import 'swiper/css/pagination';
import 'swiper/css/effect-fade';

import { homeService } from '../../services/homeService';

const HomeSlider = () => {
  const [swiperRef, setSwiperRef] = useState(null);

  const { data: sliders, isLoading, error } = useQuery({
    queryKey: ['home-sliders'],
    queryFn: homeService.getSliders,
    staleTime: 1000 * 60 * 60, 
  });

  if (isLoading) {
    return (
      <div className="w-screen h-[150px] sm:h-[300px] md:h-[400px] bg-slate-100 rounded-2xl animate-pulse flex items-center justify-center text-slate-300">
        <ImageIcon size={48} />
      </div>
    );
  }

  if (error || !sliders || sliders.length === 0) {
    return null; 
  }

  return (
    <section className="relative group md:-mt-12 w-full"> 
      <Swiper
        onSwiper={setSwiperRef}
        modules={[Autoplay, Pagination, EffectFade]}
        spaceBetween={0}
        slidesPerView={1}
        effect={'fade'} 
        speed={600}
        loop={true}
        autoplay={{
          delay: 5000,
          disableOnInteraction: false,
        }}
        pagination={{
          clickable: true,
        }}
        className="w-full h-auto overflow-hidden shadow-lg"
      >
        {sliders.map((slide) => (
          <SwiperSlide key={slide.id}>
            {/* 
              تغییر نسبت تصویر: 
              موبایل: 16/10 (تصویر کامل‌تر و بدون کراپ زیاد)
              تبلت: 16/6
              دسکتاپ: 16/4 (عریض و استاندارد)
            */}
            <div className="relative w-full aspect-[16/10] sm:aspect-[16/6] md:aspect-[16/4] bg-slate-800">
              {/* تصویر اسلایدر */}
              <img
                src={slide.image_url}
                alt={slide.name}
                className="w-full h-full object-cover"
                loading="lazy"
              />
              
              {/* لایه گرادینت */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent pointer-events-none"></div>

              {/* کپشن (متن‌ها در موبایل کمی پایین‌تر و کوچک‌تر میشن) */}
              {slide.name && (
                <div className="absolute bottom-4 right-4 md:bottom-12 md:right-16 text-white max-w-2xl animate-in fade-in slide-in-from-bottom-4 duration-700">
                  <h2 className="text-base sm:text-xl md:text-3xl font-black drop-shadow-md mb-2">
                    {slide.name}
                  </h2>
                </div>
              )}
            </div>
          </SwiperSlide>
        ))}
      </Swiper>

      {/* ================= دکمه‌های کاستوم جدید ================= */}
      {/* در موبایل ارتفاع دکمه‌ها کمتر شده (h-16) و در دسکتاپ h-24 */}

      {/* دکمه قبلی (سمت راست) */}
      <button
        onClick={() => swiperRef?.slidePrev()} 
        className="absolute z-30 right-0 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/70 text-white w-8 h-16 md:h-24 rounded-l-full flex items-center justify-center transition-all duration-300 backdrop-blur-sm opacity-0 group-hover:opacity-100 cursor-pointer translate-x-2 group-hover:translate-x-0"
        aria-label="اسلاید قبلی"
      >
         {/* آیکون در موبایل کوچکتر میشه */}
         <ChevronRight className="w-6 h-6 md:w-9 md:h-9" strokeWidth={2} />
      </button>

      {/* دکمه بعدی (سمت چپ) */}
      <button
        onClick={() => swiperRef?.slideNext()} 
        className="absolute z-30 left-0 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/70 text-white w-8 h-16 md:h-24 rounded-r-full flex items-center justify-center transition-all duration-300 backdrop-blur-sm opacity-0 group-hover:opacity-100 cursor-pointer -translate-x-2 group-hover:translate-x-0"
        aria-label="اسلاید بعدی"
      >
        <ChevronLeft className="w-6 h-6 md:w-9 md:h-9" strokeWidth={2} />
      </button>
       {/* ========================================================== */}
      
      {/* استایل‌های مربوط به pagination */}
      {/* به جای style jsx global که ممکنه در Vite ارور بده، از تگ استایل معمولی استفاده میکنیم */}
      <style>{`
        .swiper-pagination-bullet {
           width: 8px;
           height: 8px;
           background: rgba(255,255,255,0.5);
           opacity: 1;
           transition: all 0.3s ease;
        }
        .swiper-pagination-bullet-active {
          background-color: #fff !important; 
          width: 20px;
          border-radius: 4px;
        }
        /* روی موبایل بولت‌ها کمی پایین‌تر باشن که با دکمه‌ها تداخل نکنن */
        @media (max-width: 768px) {
          .swiper-pagination {
            bottom: 0px !important;
          }
          .swiper-pagination-bullet {
            width: 6px;
            height: 6px;
          }
          .swiper-pagination-bullet-active {
            width: 16px;
          }
        }
      `}</style>
    </section>
  );
};

export default HomeSlider;