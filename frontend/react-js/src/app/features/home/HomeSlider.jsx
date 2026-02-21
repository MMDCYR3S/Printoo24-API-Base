// src/app/features/home/HomeSlider.jsx
import React, { useState } from 'react'; // 👈 این خط اضافه شد
import { useQuery } from '@tanstack/react-query';
import { Swiper, SwiperSlide } from 'swiper/react';
// 👈 Navigation رو از ماژول‌ها حذف کردم چون دیگه نیازی نیست
import { Autoplay, Pagination, EffectFade } from 'swiper/modules'; 
// 👈 آیکون‌های فلش رو اضافه کردم برای دکمه‌های جدید
import { Image as ImageIcon, ChevronRight, ChevronLeft } from 'lucide-react'; 

// استایل‌های اجباری سوایپر
import 'swiper/css';
import 'swiper/css/pagination';
// import 'swiper/css/navigation'; // 👈 این دیگه لازم نیست
import 'swiper/css/effect-fade';

import { homeService } from '../../services/homeService';

const HomeSlider = () => {
  // 👈 استیت برای نگهداری رفرنس سوایپر
  const [swiperRef, setSwiperRef] = useState(null);

  const { data: sliders, isLoading, error } = useQuery({
    queryKey: ['home-sliders'],
    queryFn: homeService.getSliders,
    staleTime: 1000 * 60 * 60, 
  });

  if (isLoading) {
    return (
      <div className="w-screen h-[200px] md:h-[400px] bg-slate-100 rounded-2xl animate-pulse flex items-center justify-center text-slate-300">
        <ImageIcon size={48} />
      </div>
    );
  }

  if (error || !sliders || sliders.length === 0) {
    return null; 
  }

  return (
    // کلاس group رو اینجا داریم، پس دکمه‌ها رو تنظیم کردم فقط موقع هاور دیده بشن
    <section className="relative group md:-mt-12"> 
      <Swiper
        // 👈 اینجا رفرنس رو ذخیره می‌کنیم تا بتونیم کنترلش کنیم
        onSwiper={setSwiperRef}
        // 👈 Navigation رو از اینجا برداشتم
        modules={[Autoplay, Pagination, EffectFade]}
        spaceBetween={0}
        slidesPerView={1}
        effect={'fade'} 
        speed={600} // سرعت رو یه ذره بیشتر کردم نرم‌تر شه
        loop={true}
        autoplay={{
          delay: 5000,
          disableOnInteraction: false,
        }}
        pagination={{
          clickable: true,
          // dynamicBullets: true, // این رو برداشتم چون با دکمه‌های بزرگ بغل ممکنه شلوغ شه، خواستی برگردون
        }}
        // navigation={true} // 👈 حذف شد
        className="w-[calc(100vw-0.5rem)] h-auto overflow-hidden shadow-lg"
      >
        {sliders.map((slide) => (
          <SwiperSlide key={slide.id}>
            <div className="relative w-full aspect-[16/4] md:aspect-[16/4] bg-slate-800">
              {/* تصویر اسلایدر */}
              <img
                src={slide.image_url}
                alt={slide.name}
                className="w-full h-full object-cover"
                loading="lazy"
              />
              
              {/* لایه گرادینت */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent pointer-events-none"></div>

              {/* کپشن */}
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

      {/* ================= دکمه‌های کاستوم جدید ================= */}

      {/* دکمه قبلی (سمت راست در فارسی) */}
      <button
        onClick={() => swiperRef?.slidePrev()} // 👈 دستور حرکت به عقب
        className="absolute z-30 right-0 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/70 text-white w-8 h-24 rounded-l-full flex items-center justify-center transition-all duration-300 backdrop-blur-sm opacity-0 group-hover:opacity-100 cursor-pointer translate-x-2 group-hover:translate-x-0"
        aria-label="اسلاید قبلی"
      >
         <ChevronRight size={36} strokeWidth={2} />
      </button>

      {/* دکمه بعدی (سمت چپ در فارسی) */}
      <button
        onClick={() => swiperRef?.slideNext()} // 👈 دستور حرکت به جلو
        className="absolute z-30 left-0 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/70 text-white w-8 h-24 rounded-r-full flex items-center justify-center transition-all duration-300 backdrop-blur-sm opacity-0 group-hover:opacity-100 cursor-pointer -translate-x-2 group-hover:translate-x-0"
        aria-label="اسلاید بعدی"
      >
        <ChevronLeft size={36} strokeWidth={2} />
      </button>
       {/* ========================================================== */}
      
      {/* استایل‌های گلوبال قبلی رو پاک کردم چون دیگه لازم نیستن */}
      <style jsx global>{`
        .swiper-pagination-bullet {
           width: 10px;
           height: 10px;
           background: rgba(255,255,255,0.5);
           opacity: 1;
        }
        .swiper-pagination-bullet-active {
          background-color: var(--color-primary, #fff) !important; // رنگ پرایمری یا سفید
          width: 24px;
          border-radius: 5px;
          transition: all 0.3s ease;
        }
      `}</style>
    </section>
  );
};

export default HomeSlider;