// src/app/features/home/CategoryHero.jsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Swiper, SwiperSlide } from 'swiper/react';
import { FreeMode } from 'swiper/modules';
import { ChevronDown, Layers, Box } from 'lucide-react';

// استایل‌های سواپیر (فقط همین‌ها لازم است)
import 'swiper/css';
import 'swiper/css/free-mode';

import { categoryService } from '../../services/categoryService';
import ProductCard from '../../components/product/ProductCard';

const CategoryHero = () => {
  // فقط اولین آیتم باز باشد
  const [expandedId, setExpandedId] = useState(null);

  const { data: categories, isLoading } = useQuery({
    queryKey: ['categories-landing'],
    queryFn: categoryService.getCategoriesLanding,
  });

  // اولین بار که دیتا لود شد، اولی را باز کن
  if (!expandedId && categories?.length > 0) {
    setExpandedId(categories[0].category_info.id);
  }

  const handleToggle = (id) => {
    // اگر روی باز کلیک کرد ببنده، اگر روی بسته کلیک کرد باز کنه
    setExpandedId(expandedId === id ? null : id);
  };

  if (isLoading) return <HeroSkeleton />;

  return (
    <section className="container mx-auto px-4 my-8">
      <div className="flex flex-col gap-4">
        {categories?.map((catData) => {
          const { category_info, sub_categories, products } = catData;
          const isOpen = expandedId === category_info.id;

          return (
            <motion.div
              key={category_info.id}
              layout // این پراپ جادویی است: تغییر سایز را انیمیت می‌کند
              initial={{ borderRadius: 16 }}
              className={`overflow-hidden border transition-colors duration-300 ${
                isOpen ? 'bg-white border-primary/20 shadow-lg' : 'bg-white border-base-200 hover:border-base-300'
              }`}
            >
              {/* --- HEADER (ACCORDION TRIGGER) --- */}
              <motion.div
                layout="position"
                onClick={() => handleToggle(category_info.id)}
                className="relative cursor-pointer h-20 md:h-24 flex items-center px-6 group overflow-hidden"
              >
                {/* تصویر بنر پس‌زمینه (Wide) با افکت تاریک */}
                <div className="absolute inset-0 z-0">
                  <img 
                    src={category_info.banners?.wide} 
                    alt={category_info.name}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                  />
                  {/* گرادینت روی عکس برای خوانایی متن */}
                  <div className={`absolute inset-0 transition-opacity duration-300 ${isOpen ? 'bg-slate-900/80' : 'bg-slate-900/60 group-hover:bg-slate-900/70'}`} />
                </div>

                <div className="relative z-10 flex items-center justify-between w-full text-white">
                  <div className="flex items-center gap-4">
                    {/* آیکون یا تصویر کوچک باکس */}
                    <div className="w-12 h-12 rounded-lg bg-white/10 backdrop-blur-md flex items-center justify-center border border-white/20">
                      <img 
                        src={category_info.banners?.box} 
                        className="w-full h-full object-cover rounded-lg opacity-90"
                        alt=""
                        onError={(e) => { e.target.style.display='none'; }}
                      />
                      <Box className="absolute text-white/50" size={20} />
                    </div>
                    
                    <div>
                      <h2 className="text-xl md:text-2xl font-black tracking-tight">{category_info.name}</h2>
                      {isOpen && (
                        <motion.p 
                          initial={{ opacity: 0, y: 5 }} 
                          animate={{ opacity: 1, y: 0 }}
                          className="text-xs text-white/70 font-medium hidden md:block"
                        >
                          {category_info.description}
                        </motion.p>
                      )}
                    </div>
                  </div>

                  <ChevronDown 
                    size={24} 
                    className={`transition-transform duration-300 ${isOpen ? 'rotate-180 text-secondary' : 'text-white/70'}`} 
                  />
                </div>
              </motion.div>

              {/* --- CONTENT (EXPANDABLE) --- */}
              <AnimatePresence>
                {isOpen && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                  >
                    <div className="p-4 md:p-6 flex flex-col gap-8">
                      
                      {/* 1. باکس زیر دسته‌ها */}
                      {sub_categories?.length > 0 && (
                        <div>
                          <div className="flex items-center gap-2 mb-4 opacity-70">
                            <Layers size={18} className="text-primary"/>
                            <span className="text-sm font-bold text-base-content">زیر دسته‌های {category_info.name}</span>
                          </div>
                          
                          <div className="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-7 gap-3 md:gap-4">
                            {sub_categories.map((sub, idx) => (
                              <div key={idx} className="group cursor-pointer flex flex-col gap-2">
                                <div className="aspect-square rounded-2xl border border-base-200 overflow-hidden bg-base-50 relative group-hover:border-primary group-hover:shadow-md transition-all">
                                  <img 
                                    src={sub.thumbnail} 
                                    alt={sub.name}
                                    loading="lazy"
                                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                                  />
                                </div>
                                <span className="text-xs md:text-sm font-bold text-center text-base-content/80 group-hover:text-primary transition-colors line-clamp-2">
                                  {sub.name}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* 2. لاین اسلایدر محصولات (Swiper Rail) */}
                      {products?.length > 0 && (
                        <div className="bg-base-50 p-4 rounded-2xl border border-base-200/50">
                          <div className="flex items-center justify-between mb-4">
                             <span className="text-sm font-bold text-base-content/70">محصولات منتخب</span>
                             <button className="btn btn-xs btn-link no-underline text-secondary">مشاهده همه</button>
                          </div>
                          
                          <Swiper
                            modules={[FreeMode]}
                            spaceBetween={16}
                            slidesPerView={1.5} // در موبایل ۱.۵ تا دیده بشه که بفهمه ادامه‌داره
                            freeMode={true}
                            breakpoints={{
                              640: { slidesPerView: 2.5 },
                              1024: { slidesPerView: 4.5 },
                              1280: { slidesPerView: 5.5 },
                            }}
                            className="!pb-4" // برای سایه کارت‌ها
                          >
                            {products.map((product) => (
                              <SwiperSlide key={product.id}>
                                <ProductCard product={product} />
                              </SwiperSlide>
                            ))}
                          </Swiper>
                        </div>
                      )}

                      {(!sub_categories?.length && !products?.length) && (
                        <div className="text-center py-8 text-base-content/40 text-sm">
                          محتوایی برای نمایش وجود ندارد.
                        </div>
                      )}

                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
};

// اسکلتون برای زمان لودینگ (خیلی مهمه برای حس سرعت)
const HeroSkeleton = () => (
  <div className="container mx-auto px-4 my-8 space-y-4">
    {[1, 2, 3].map((i) => (
      <div key={i} className="h-24 bg-base-200 rounded-2xl animate-pulse"></div>
    ))}
  </div>
);

export default CategoryHero;