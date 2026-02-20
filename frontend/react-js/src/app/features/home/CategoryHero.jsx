// src/app/features/home/CategoryHero.jsx
import { useState, useEffect, memo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Swiper, SwiperSlide } from 'swiper/react';
import { FreeMode } from 'swiper/modules';
import { ChevronDown, Sparkles, LayoutGrid, Tag, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import 'swiper/css';
import 'swiper/css/free-mode';

import { categoryService } from '../../services/categoryService';
import ProductCard from '../../components/product/ProductCard';

const CategoryItem = memo(({ category, isOpen, onToggle }) => {
  const { category_info, sub_categories, products } = category;
  
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    let timer;
    if (isOpen && !showContent) {
      timer = setTimeout(() => {
        setShowContent(true);
      }, 350);
    }
    return () => clearTimeout(timer);
  }, [isOpen, showContent]);

  return (
    <div
      className={`rounded-2xl overflow-hidden  transition-all duration-300  ${
        isOpen 
          ? '   ring-1 ring-primary/5' 
          : ' ring-1 ring-primary/5'
      }`}
    >
      <div
        onClick={() => onToggle(category_info.id)}
        className={`relative cursor-pointer h-16 md:h-20 flex items-center px-4 md:px-6 select-none overflow-hidden transition-all ${isOpen ? 'rounded-t-2xl' : 'rounded-2xl'}`}
      >
        <div className="absolute inset-0 z-0 bg-base">
           <img 
            src={category_info.banners?.wide} 
            alt=""
            loading="lazy"
            className={`w-full h-full object-cover transition-opacity duration-500 ${isOpen ? 'opacity-40' : 'opacity-0 group-hover:opacity-100'}`}
          />
          <div className={`absolute inset-0 transition-colors duration-300  ${isOpen ? 'bg-primary /90' : ' group-hover:bg-slate-900/70'}`} />
        </div>

        <div className={`relative z-10 flex items-center justify-between w-full transition-colors duration-300 ${isOpen ? 'text-white' : 'text-slate-700'}`}>
          <div className="flex items-center gap-4">
             <div className={`w-10 h-10 md:w-12 md:h-12 rounded-xl flex items-center justify-center overflow-hidden border transition-all ${isOpen ? 'border-white/30 bg-white/10 backdrop-blur-sm' : 'border-slate-100 bg-slate-50'}`}>
               <img 
                 src={category_info.banners?.box} 
                 className="w-full h-full object-cover"
                 alt=""
                 onError={(e) => { e.target.style.display='none'; }}
               />
             </div>
             
             <div className="flex flex-col">
               <div className="flex items-center gap-2">
                 <h2 className="text-lg md:text-xl font-black tracking-tight">{category_info.name}</h2>
               </div>
               <p className={`text-xs mt-1 font-medium transition-all duration-300 hidden md:block ${isOpen ? 'text-slate-200 opacity-100' : 'opacity-0 -translate-y-2'}`}>
                 {category_info.description}
               </p>
             </div>
          </div>

          <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${isOpen ? 'bg-white text-primary rotate-180' : 'bg-slate-100 text-slate-400'}`}>
             <ChevronDown size={32} />
          </div>
        </div>
      </div>

      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            <div className="p-4 md:p-4 bg-base border-t border-slate-100/10 min-h-[200px]">
              
              {!showContent ? (
                 <ContentSkeleton />
              ) : (
                <div className="flex flex-col gap-8 animate-in fade-in duration-500">
                  
                  {sub_categories?.length > 0 && (
                    <section>
                      <div className="flex items-center gap-2 mb-4 px-1">
                        <div className="p-1.5 bg-blue-100 text-blue-600 rounded-lg">
                           <LayoutGrid size={16} />
                        </div>
                        <h3 className="text-sm font-black text-slate-700">زیر دسته بندی ها</h3>
                      </div>
                      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-6 gap-3 md:gap-4">
                        {sub_categories.map((sub, idx) => (
                          <Link 
                            key={idx} 
                            to={`/shop?category=${sub.slug}`} 
                            className="group cursor-pointer flex flex-col items-center gap-2"
                          >
                            <div className="relative w-full aspect-square rounded-2xl bg-white hover:shadow-xl  shadow-black/10  transition-all duration-300 overflow-hidden">
                              <img src={sub.thumbnail} alt={sub.name} loading="lazy" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                            </div>
                            <span className="text-[11px] md:text-xs font-bold text-center text-slate-500 group-hover:text-slate-800 transition-colors">
                              {sub.name}
                            </span>
                          </Link>
                        ))}
                      </div>
                    </section>
                  )}

                  {products?.length > 0 && (
                    <section className="relative">
                      <div className="flex items-center justify-between mb-4 px-1">
                        <div className="flex items-center gap-2">
                            <div className="p-1.5 bg-emerald-100 text-emerald-600 rounded-lg">
                              <Tag size={16} />
                            </div>
                            <h3 className="text-sm font-black text-slate-700">محصولات برگزیده</h3>
                        </div>
                        <Link 
                          to={`/shop?category=${category_info.slug}`} 
                          className="text-xs font-bold text-primary hover:text-primary-focus flex items-center gap-1"
                        >
                           مشاهده همه <ArrowLeft size={14} />
                        </Link>
                      </div>

                      <div className="-mr-4 md:mr-0 pr-4 md:pr-0">
                        <Swiper
                          modules={[FreeMode]}
                          spaceBetween={16}
                          slidesPerView={1.3}
                          freeMode={true}
                          breakpoints={{
                            500: { slidesPerView: 2.2 },
                            768: { slidesPerView: 3.2 },
                            1024: { slidesPerView: 4.2 },
                            1280: { slidesPerView: 5.2 },
                          }}
                          className="!pb-6 !pt-2 px-1"
                        >
                          {products.map((product) => (
                            <SwiperSlide key={product.id} className="h-auto">
                              <ProductCard product={product} />
                            </SwiperSlide>
                          ))}
                        </Swiper>
                      </div>
                    </section>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});

const CategoryHero = () => {
  const [expandedId, setExpandedId] = useState(null);

  const { data: categories, isLoading } = useQuery({
    queryKey: ['categories-landing'],
    queryFn: categoryService.getCategoriesLanding,
  });

  if (expandedId === null && categories?.length > 0) {
    setExpandedId(categories[0].category_info.id);
  }

  const handleToggle = (id) => {
    setExpandedId(prev => prev === id ? null : id);
  };

  if (isLoading) return <HeroSkeleton />;

  return (
    <section className="container mx-auto px-4 my-6">
      <div className="flex flex-col gap-4">
        {categories?.map((catData) => (
          <CategoryItem 
            key={catData.category_info.id} 
            category={catData} 
            isOpen={expandedId === catData.category_info.id}
            onToggle={handleToggle}
          />
        ))}
      </div>
    </section>
  );
};

const ContentSkeleton = () => (
  <div className="flex flex-col gap-8 animate-pulse">
    <div className="space-y-4">
       <div className="h-6 w-32 bg-slate-200 rounded"></div>
       <div className="grid grid-cols-4 gap-4">
          {[1,2,3,4].map(i => <div key={i} className="aspect-square bg-slate-200 rounded-2xl"></div>)}
       </div>
    </div>
    <div className="space-y-4">
       <div className="flex justify-between">
          <div className="h-6 w-40 bg-slate-200 rounded"></div>
       </div>
       <div className="flex gap-4 overflow-hidden">
          {[1,2,3].map(i => <div key={i} className="w-60 h-40 shrink-0 bg-slate-200 rounded-2xl"></div>)}
       </div>
    </div>
  </div>
);

const HeroSkeleton = () => (
  <section className="container mx-auto px-4 my-6 space-y-4">
    {[1, 2, 3].map((i) => (
      <div key={i} className="rounded-2xl bg-white border border-slate-200 overflow-hidden">
        <div className="h-20 bg-slate-100 animate-pulse flex items-center px-6 gap-4">
           <div className="w-12 h-12 bg-slate-300 rounded-xl"></div>
           <div className="flex-1 space-y-2">
              <div className="h-4 w-40 bg-slate-300 rounded"></div>
              <div className="h-3 w-64 bg-slate-200 rounded hidden md:block"></div>
           </div>
        </div>
      </div>
    ))}
  </section>
);

export default CategoryHero;