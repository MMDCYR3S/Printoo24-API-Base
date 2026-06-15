// src/app/features/home/CategoryHero.jsx
import { useState, useEffect, memo, useCallback, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Swiper, SwiperSlide } from 'swiper/react';
import { FreeMode } from 'swiper/modules';
import { ChevronDown, LayoutGrid, Tag, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import 'swiper/css';
import 'swiper/css/free-mode';

import { categoryService } from '../../services/categoryService';
import ProductCard from '../../components/product/ProductCard';

/* ─────────────────────────────────────────────
   Variants
   ───────────────────────────────────────────── */
const staggerContainer = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.1 },
  },
};

const staggerItem = {
  hidden: { opacity: 0, y: 14, scale: 0.95 },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: 'spring', stiffness: 260, damping: 24 },
  },
};

const expandVariants = {
  collapsed: { height: 0, opacity: 0 },
  expanded: {
    height: 'auto',
    opacity: 1,
    transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] },
  },
  exit: {
    height: 0,
    opacity: 0,
    transition: { duration: 0.28, ease: [0.22, 1, 0.36, 1] },
  },
};

/* ─────────────────────────────────────────────
   LazyImage — با shimmer، fade-in، و cache-hit
   ───────────────────────────────────────────── */
const LazyImage = memo(({ src, alt, className, priority = false, onError }) => {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);
  const imgRef = useRef(null);

  // تصویر از cache — load event fire نمی‌شه
  useEffect(() => {
    if (imgRef.current?.complete && imgRef.current.naturalWidth > 0) {
      setLoaded(true);
    }
  }, []);

  return (
    <div className="relative w-full h-full bg-slate-100 overflow-hidden">
      {!loaded && !error && (
        <div className="absolute inset-0 bg-slate-100 animate-pulse" />
      )}

      {!error && src && (
        <img
          ref={imgRef}
          src={src}
          alt={alt}
          loading={priority ? 'eager' : 'lazy'}
          decoding="async"
          fetchPriority={priority ? 'high' : 'low'}
          className={`${className} transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}
          onLoad={() => setLoaded(true)}
          onError={(e) => {
            setError(true);
            onError?.(e);
          }}
        />
      )}
    </div>
  );
});
LazyImage.displayName = 'LazyImage';

/* ─────────────────────────────────────────────
   AccordionContent — محتوای داخل accordion
   فقط بعد از اولین باز شدن mount می‌شه،
   بعدش هیچ‌وقت unmount نمی‌شه (re-fetch نداریم)
   ───────────────────────────────────────────── */
const AccordionContent = memo(({ category, isFirstAndOpen }) => {
  const { category_info, sub_categories, products } = category;

  return (
    <div className="flex flex-col gap-7">

      {/* Sub-categories Grid */}
      {sub_categories?.length > 0 && (
        <section>
          <div className="flex items-center gap-2.5 mb-4 px-0.5">
            <div className="p-1.5 bg-blue-50 text-blue-500 rounded-lg">
              <LayoutGrid size={15} strokeWidth={2.2} />
            </div>
            <h3 className="text-[13px] font-bold text-slate-600">ژێر پۆل</h3>
          </div>

          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="show"
            className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-6 gap-3 md:gap-4"
          >
            {sub_categories.map((sub, idx) => (
              <motion.div key={sub.id ?? idx} variants={staggerItem}>
                <Link
                  to={`/shop?category=${sub.slug}`}
                  className="group flex flex-col items-center gap-2"
                >
                  <div className="
                    relative w-full aspect-square rounded-2xl bg-white overflow-hidden
                    ring-1 ring-black/[0.05]
                    transition-all duration-300
                    group-hover:shadow-lg group-hover:shadow-black/8 group-hover:ring-primary/20
                    group-hover:-translate-y-0.5
                  ">
                    <LazyImage
                      src={sub.thumbnail}
                      alt={sub.name}
                      className="w-full h-full object-cover transition-transform duration-500 ease-out group-hover:scale-[1.06]"
                      priority={isFirstAndOpen && idx < 6}
                    />
                  </div>
                  <span className="
                    text-[11px] md:text-xs font-semibold text-center
                    text-slate-500 group-hover:text-slate-800
                    transition-colors duration-200 leading-tight
                  ">
                    {sub.name}
                  </span>
                </Link>
              </motion.div>
            ))}
          </motion.div>
        </section>
      )}

      {/* Featured Products Carousel */}
      {products?.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-4 px-0.5">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 bg-emerald-50 text-emerald-500 rounded-lg">
                <Tag size={15} strokeWidth={2.2} />
              </div>
              <h3 className="text-[13px] font-bold text-slate-600">بەرهەمە تایبەتەکان</h3>
            </div>
            <Link
              to={`/shop?category=${category_info.slug}`}
              className="
                text-xs font-bold text-primary/80 hover:text-primary
                flex items-center gap-1 transition-all duration-200
                hover:gap-2
              "
            >
              بینینی هەمووی <ArrowLeft size={13} />
            </Link>
          </div>

          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="-mr-4 md:mr-0 pr-4 md:pr-0"
          >
            <Swiper
              modules={[FreeMode]}
              spaceBetween={14}
              slidesPerView={1.35}
              freeMode={{ enabled: true, momentum: true, momentumRatio: 0.6 }}
              breakpoints={{
                500:  { slidesPerView: 2.2, spaceBetween: 14 },
                768:  { slidesPerView: 3.2, spaceBetween: 16 },
                1024: { slidesPerView: 4.2, spaceBetween: 16 },
                1280: { slidesPerView: 5.2, spaceBetween: 18 },
              }}
              className="!pb-4 !pt-1 px-0.5"
            >
              {products.map((product) => (
                <SwiperSlide key={product.id} className="h-auto">
                  <ProductCard product={product} />
                </SwiperSlide>
              ))}
            </Swiper>
          </motion.div>
        </section>
      )}
    </div>
  );
});
AccordionContent.displayName = 'AccordionContent';

/* ─────────────────────────────────────────────
   CategoryItem
   ───────────────────────────────────────────── */
const CategoryItem = memo(({ category, isOpen, onToggle, index }) => {
  const { category_info, sub_categories, products } = category;

  // بعد از اولین باز شدن، محتوا همیشه mount می‌مونه
  const [hasBeenOpened, setHasBeenOpened] = useState(isOpen);

  useEffect(() => {
    if (isOpen && !hasBeenOpened) setHasBeenOpened(true);
  }, [isOpen, hasBeenOpened]);

  const isFirstAndOpen = index === 0 && isOpen;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.07, duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className={`
        relative rounded-[20px] overflow-hidden transition-all duration-500
        ${isOpen
          ? 'shadow-[0_8px_40px_-8px_rgba(0,0,0,0.12)] ring-1 ring-black/[0.04]'
          : 'shadow-sm ring-1 ring-black/[0.06] hover:shadow-md hover:ring-black/[0.08]'
        }
      `}
    >
      {/* ── Header ── */}
      <button
        onClick={() => onToggle(category_info.id)}
        aria-expanded={isOpen}
        aria-controls={`accordion-content-${category_info.id}`}
        className={`
          relative w-full cursor-pointer flex items-center gap-4 px-4 md:px-6
          h-[68px] md:h-[76px] select-none overflow-hidden
          transition-all duration-500
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40
          ${isOpen ? 'rounded-t-[20px]' : 'rounded-[20px]'}
        `}
      >
        {/* Background */}
        <div className="absolute inset-0 z-0" aria-hidden="true">
          <div className={`absolute inset-0 transition-colors duration-500 ${isOpen ? 'bg-black' : 'bg-base'}`} />
          {isOpen && category_info.banners?.wide && (
            <img
              src={category_info.banners.wide}
              alt=""
              role="presentation"
              loading="lazy"
              decoding="async"
              fetchPriority="low"
              className="absolute inset-0 w-full h-full object-cover opacity-20 scale-105 blur-[1px]"
            />
          )}
        </div>

        {/* Content */}
        <div className="relative z-10 flex items-center justify-between w-full">
          <div className="flex items-center gap-3 md:gap-4 min-w-0">
            {/* Thumbnail */}
            <div className={`
              shrink-0 w-11 h-11 md:w-[50px] md:h-[50px] rounded-2xl overflow-hidden
              flex items-center justify-center
              transition-all duration-500
              ${isOpen
                ? 'bg-white/15 backdrop-blur-md ring-1 ring-white/20 shadow-lg shadow-black/10'
                : 'bg-slate-50 ring-1 ring-slate-200/60'
              }
            `}>
              <LazyImage
                src={category_info.banners?.box}
                alt={category_info.name}
                className="w-full h-full object-cover"
                priority={index < 2}
              />
            </div>

            {/* Text */}
            <div className="flex flex-col min-w-0">
              <h2 className={`
                text-[15px] md:text-lg font-extrabold tracking-tight truncate
                transition-colors duration-400
                ${isOpen ? 'text-white' : 'text-slate-800'}
              `}>
                {category_info.name}
              </h2>

              {/* description فقط موقع open نشون داده می‌شه — بدون height animate مشکل‌دار */}
              <AnimatePresence initial={false}>
                {isOpen && category_info.description && (
                  <motion.p
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    transition={{ duration: 0.25 }}
                    className="text-[11px] md:text-xs font-medium text-white/70 leading-relaxed hidden md:block"
                  >
                    {category_info.description}
                  </motion.p>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Chevron */}
          <div className={`
            shrink-0 w-8 h-8 md:w-9 md:h-9 rounded-full flex items-center justify-center
            transition-all duration-500 ease-out
            ${isOpen
              ? 'bg-white text-primary rotate-180 shadow-md shadow-black/10'
              : 'bg-slate-100 text-slate-400 hover:bg-slate-200'
            }
          `}>
            <ChevronDown size={18} strokeWidth={2.5} />
          </div>
        </div>
      </button>

      {/* ── Expandable Content ── */}
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            id={`accordion-content-${category_info.id}`}
            role="region"
            variants={expandVariants}
            initial="collapsed"
            animate="expanded"
            exit="exit"
            className="overflow-hidden"
          >
            <div className="p-4 md:p-6 bg-base border-t border-slate-100 min-h-[180px]">
              {hasBeenOpened ? (
                <AccordionContent
                  category={category}
                  isFirstAndOpen={isFirstAndOpen}
                />
              ) : (
                <ContentSkeleton />
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});
CategoryItem.displayName = 'CategoryItem';

/* ─────────────────────────────────────────────
   CategoryHero
   ───────────────────────────────────────────── */
const CategoryHero = () => {
  const [expandedId, setExpandedId] = useState(null);

  const { data: categories, isLoading } = useQuery({
    queryKey: ['categories-landing'],
    queryFn: categoryService.getCategoriesLanding,
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 30,
  });

  useEffect(() => {
    if (expandedId === null && categories?.length > 0) {
      setExpandedId(categories[0].category_info.id);
    }
  }, [categories, expandedId]);

  const handleToggle = useCallback((id) => {
    setExpandedId((prev) => (prev === id ? null : id));
  }, []);

  if (isLoading) return <HeroSkeleton />;

  return (
    <section className="container mx-auto px-4 my-8">
      <div className="flex flex-col gap-3 md:gap-4">
        {categories?.map((catData, index) => (
          <CategoryItem
            key={catData.category_info.id}
            category={catData}
            isOpen={expandedId === catData.category_info.id}
            onToggle={handleToggle}
            index={index}
          />
        ))}
      </div>
    </section>
  );
};

/* ─────────────────────────────────────────────
   Skeletons
   ───────────────────────────────────────────── */
const shimmer =
  'relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_1.8s_infinite] before:bg-gradient-to-r before:from-transparent before:via-white/40 before:to-transparent';

const ContentSkeleton = () => (
  <div className="flex flex-col gap-7">
    <div className="space-y-4">
      <div className={`h-5 w-28 bg-slate-100 rounded-lg ${shimmer}`} />
      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3 md:gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="flex flex-col items-center gap-2">
            <div className={`w-full aspect-square bg-slate-100 rounded-2xl ${shimmer}`} />
            <div className={`h-3 w-12 bg-slate-100 rounded ${shimmer}`} />
          </div>
        ))}
      </div>
    </div>
    <div className="space-y-4">
      <div className="flex justify-between">
        <div className={`h-5 w-32 bg-slate-100 rounded-lg ${shimmer}`} />
        <div className={`h-4 w-16 bg-slate-100 rounded ${shimmer}`} />
      </div>
      <div className="flex gap-3.5 overflow-hidden">
        {[1, 2, 3].map((i) => (
          <div key={i} className={`w-56 h-44 shrink-0 bg-slate-100 rounded-2xl ${shimmer}`} />
        ))}
      </div>
    </div>
  </div>
);

const HeroSkeleton = () => (
  <section className="container mx-auto px-4 my-8 space-y-3 md:space-y-4">
    {[1, 2, 3].map((i) => (
      <div
        key={i}
        className="rounded-[20px] bg-base ring-1 ring-black/[0.06] overflow-hidden"
      >
        <div className="h-[68px] md:h-[76px] flex items-center px-4 md:px-6 gap-3 md:gap-4">
          <div className={`w-11 h-11 md:w-[50px] md:h-[50px] bg-slate-100 rounded-2xl ${shimmer}`} />
          <div className="flex-1 space-y-2.5">
            <div className={`h-4 w-36 bg-slate-100 rounded-lg ${shimmer}`} />
            <div className={`h-3 w-56 bg-slate-50 rounded hidden md:block ${shimmer}`} />
          </div>
          <div className={`w-8 h-8 md:w-9 md:h-9 bg-slate-100 rounded-full ${shimmer}`} />
        </div>
      </div>
    ))}
  </section>
);

export default CategoryHero;