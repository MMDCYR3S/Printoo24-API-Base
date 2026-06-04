// src/app/components/layout/MegaMenu.jsx
import { useState, useEffect, useCallback, useRef, memo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ArrowLeft, Image as ImageIcon, Layers } from 'lucide-react';
import { categoryService } from '../../services/categoryService';
import pageText from '../../lang/pages.json';

/* ─────────────────────────────────────────────
   انیمیشن‌های stagger برای آیتم‌های گرید
   ───────────────────────────────────────────── */
const gridContainer = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.025, delayChildren: 0.05 },
  },
};

const gridItem = {
  hidden: { opacity: 0, y: 10, scale: 0.96 },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: 'spring', stiffness: 300, damping: 26 },
  },
};

const sidebarItem = {
  hidden: { opacity: 0, x: 12 },
  show: { opacity: 1, x: 0 },
};

const sidebarContainer = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.03, delayChildren: 0.08 },
  },
};

/* ─────────────────────────────────────────────
   LazyImage — با shimmer، fade-in، و cache-hit
   (همان پترن CategoryHero)
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
   MegaMenu — کامپوننت اصلی
   ───────────────────────────────────────────── */
const MegaMenu = ({ isOpen, onClose }) => {
  const [activeId, setActiveId] = useState(null);
  const [hasOpenedOnce, setHasOpenedOnce] = useState(false);
  const navigate = useNavigate();
  const contentRef = useRef(null);

  useEffect(() => {
    if (isOpen && !hasOpenedOnce) setHasOpenedOnce(true);
  }, [isOpen, hasOpenedOnce]);

  const { data: categories, isLoading } = useQuery({
    queryKey: ['categories-tree'],
    queryFn: categoryService.getCategoriesTree,
    staleTime: 1000 * 60 * 60,
    enabled: hasOpenedOnce,
  });

  useEffect(() => {
    if (categories?.length > 0 && !activeId) setActiveId(categories[0].id);
  }, [categories, activeId]);

  // اسکرول به بالا هنگام تغییر دسته‌بندی
  useEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [activeId]);

  const handleParentClick = useCallback(
    (slug) => {
      navigate(`/shop?category=${slug}`);
      if (onClose) onClose();
    },
    [navigate, onClose]
  );

  if (!hasOpenedOnce && !categories) return null;

  const activeCategory =
    categories?.find((c) => c.id === activeId) || categories?.[0];

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
          className="
            absolute top-full right-0 left-0 z-50
            bg-white/[0.98] backdrop-blur-xl
            shadow-[0_20px_60px_-10px_rgba(0,0,0,0.15)]
            rounded-b-2xl
            border-t border-slate-200/60
            overflow-hidden flex h-[70vh]
          "
        >
          {isLoading ? (
            <MegaMenuSkeleton />
          ) : (
            <>
              {/* ── سایدبار ── */}
              <div className="w-[230px] flex-shrink-0 bg-radial from-white to-slate-200 border-l border-slate-200/40 overflow-y-auto custom-scrollbar">
                <div className="py-3 px-2.5">
                  {/* عنوان سایدبار */}
                  <div className="flex items-center gap-2 px-3 py-2 mb-1">
                    <Layers size={14} className="text-primary" />
                    <span className="text-[11px] font-bold text-primary tracking-wide">
                      {pageText.profile.orderDetailPage.specLabels.category}
                    </span>
                  </div>

                  <motion.ul
                    variants={sidebarContainer}
                    initial="hidden"
                    animate="show"
                    className="space-y-0.5"
                  >
                    {categories?.map((cat) => {
                      const isActive = activeId === cat.id;
                      return (
                        <motion.li key={cat.id} variants={sidebarItem}>
                          <button
                            onMouseEnter={() => setActiveId(cat.id)}
                            onClick={() => handleParentClick(cat.slug)}
                            className={`
                              group w-full flex items-center justify-between
                              px-3 py-2.5 rounded-xl text-[13px]
                              transition-all duration-200 ease-out
                              focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30
                              ${isActive
                                ? 'bg-primary text-white font-bold shadow-md shadow-primary/20'
                                : 'text-slate-600 hover:bg-white hover:shadow-sm font-medium'
                              }
                            `}
                          >
                            <span className="truncate">{cat.name}</span>
                            <ChevronLeft
                              size={13}
                              className={`
                                transition-all duration-200
                                ${isActive
                                  ? 'text-white/80 opacity-100'
                                  : 'text-slate-300 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0'
                                }
                              `}
                            />
                          </button>
                        </motion.li>
                      );
                    })}
                  </motion.ul>
                </div>
              </div>

              {/* ── بدنه اصلی ── */}
              <div
                ref={contentRef}
                className="flex-1 overflow-y-auto custom-scrollbar"
              >
                <AnimatePresence mode="wait">
                  {activeCategory && (
                    <motion.div
                      key={activeCategory.id}
                      initial={{ opacity: 0, x: -12 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 12 }}
                      transition={{ duration: 0.2, ease: 'easeOut' }}
                      className="p-6"
                    >
                      {/* هدر */}
                      <div className="flex items-center justify-between mb-5 pb-3 border-b border-slate-100">
                        <h3 className="text-base font-extrabold text-slate-800 flex items-center gap-2.5">
                          <span className="w-1 h-5 bg-gradient-to-b from-primary to-primary/50 rounded-full" />
                          {activeCategory.name}
                          {activeCategory.children?.length > 0 && (
                            <span className="text-[11px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                              {activeCategory.children.length} {pageText.home.categoryHero.subC}
                            </span>
                          )}
                        </h3>
                        <Link
                          to={`/shop?category=${activeCategory.slug}`}
                          onClick={onClose}
                          className="
                            text-xs font-bold text-primary/70 hover:text-primary
                            flex items-center gap-1.5
                            px-3 py-1.5 rounded-lg
                            hover:bg-primary/5
                            transition-all duration-200
                          "
                        >
                          مشاهده همه
                          <ArrowLeft size={13} />
                        </Link>
                      </div>

                      {/* گرید زیردسته‌ها */}
                      {activeCategory.children?.length > 0 ? (
                        <motion.div
                          variants={gridContainer}
                          initial="hidden"
                          animate="show"
                          className="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-7 gap-3"
                        >
                          {activeCategory.children.map((sub, idx) => (
                            <motion.div key={sub.id} variants={gridItem}>
                              <Link
                                to={`/shop?category=${sub.slug}`}
                                onClick={onClose}
                                className="
                                  group flex flex-col items-center gap-2.5
                                  p-2.5 rounded-2xl
                                  transition-all duration-300 ease-out
                                  hover:bg-slate-50
                                  border border-transparent hover:border-slate-200/80
                                  hover:shadow-sm
                                "
                              >
                                {/* تصویر — LazyImage با shimmer و fade-in */}
                                <div className="
                                  relative w-full aspect-square overflow-hidden rounded-xl
                                  ring-1 ring-black/[0.04]
                                  group-hover:ring-primary/20
                                  group-hover:shadow-md group-hover:shadow-primary/5
                                  transition-all duration-300
                                ">
                                  {sub.thumbnail ? (
                                    <LazyImage
                                      src={sub.thumbnail}
                                      alt={sub.name}
                                      className="w-full h-full object-cover transition-transform duration-500 ease-out group-hover:scale-[1.06]"
                                      priority={idx < 7}
                                    />
                                  ) : (
                                    <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
                                      <ImageIcon
                                        size={20}
                                        className="text-slate-300 group-hover:text-slate-400 transition-colors"
                                      />
                                    </div>
                                  )}
                                </div>

                                {/* اسم */}
                                <span className="
                                  text-[11px] font-semibold text-center leading-[1.4]
                                  text-slate-500 group-hover:text-slate-800
                                  transition-colors duration-200
                                  line-clamp-2 h-8 flex items-center justify-center
                                ">
                                  {sub.name}
                                </span>
                              </Link>
                            </motion.div>
                          ))}
                        </motion.div>
                      ) : (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="flex flex-col items-center justify-center h-48 gap-3"
                        >
                          <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center">
                            <Layers size={24} className="text-slate-300" />
                          </div>
                          <p className="text-sm text-slate-400 font-medium">
                            {pageText.home.categoryHero.subC} 0
                          </p>
                        </motion.div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
};

/* ─────────────────────────────────────────────
   Skeleton — با افکت shimmer
   ───────────────────────────────────────────── */
const shimmer =
  'relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_1.8s_infinite] before:bg-gradient-to-r before:from-transparent before:via-white/50 before:to-transparent';

const MegaMenuSkeleton = () => (
  <div className="flex w-full h-full bg-white/[0.98]">
    {/* سایدبار */}
    <div className="w-[230px] bg-slate-50/80 border-l border-slate-200/40 p-3 space-y-1.5">
      <div className={`h-4 w-20 bg-slate-100 rounded-lg mb-3 ${shimmer}`} />
      {[...Array(10)].map((_, i) => (
        <div
          key={i}
          className={`h-9 bg-slate-100/80 rounded-xl ${shimmer}`}
          style={{ animationDelay: `${i * 80}ms`, width: `${70 + Math.random() * 30}%` }}
        />
      ))}
    </div>
    {/* بدنه */}
    <div className="flex-1 p-6 space-y-5">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div className={`h-5 w-36 bg-slate-100 rounded-lg ${shimmer}`} />
        <div className={`h-4 w-20 bg-slate-50 rounded-lg ${shimmer}`} />
      </div>
      <div className="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-7 gap-3">
        {[...Array(14)].map((_, i) => (
          <div key={i} className="flex flex-col items-center gap-2.5 p-2.5">
            <div
              className={`w-full aspect-square bg-slate-100/80 rounded-xl ${shimmer}`}
              style={{ animationDelay: `${i * 50}ms` }}
            />
            <div className={`h-3 w-14 bg-slate-100/60 rounded ${shimmer}`} />
          </div>
        ))}
      </div>
    </div>
  </div>
);

export default MegaMenu;