import { useState, useMemo, useCallback, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { shopService } from '../../services/shopService';
import { categoryService } from '../../services/categoryService';
import ProductCard from '../../components/product/ProductCard';
import ShopSidebar from './components/ShopSidebar';
import {
  Search,
  Filter,
  X,
  ChevronLeft,
  ChevronRight,
  SlidersHorizontal,
  PackageOpen,
  Sparkles,
  ArrowLeft,
} from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import clsx from 'clsx';
import pageText from '../../lang/pages.json';

const ITEMS_PER_PAGE = 12;

/* ─────────────────────────────────────────────
   انیمیشن‌ها
   ───────────────────────────────────────────── */
const staggerGrid = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05, delayChildren: 0.02 },
  },
};

const gridItemAnim = {
  hidden: { opacity: 0, y: 16, scale: 0.97 },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: 'spring', stiffness: 260, damping: 24 },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.15 },
  },
};

/* ─────────────────────────────────────────────
   ShopPage
   ───────────────────────────────────────────── */
const ShopPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [localSearch, setLocalSearch] = useState(searchParams.get('search') || '');
  const gridRef = useRef(null);

  const selectedSlugs = searchParams.getAll('category');
  const searchQuery = searchParams.get('search');
  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  /* ── دیتا ── */
  const { data: categoriesTree = [] } = useQuery({
    queryKey: ['categories-tree'],
    queryFn: categoryService.getCategoriesTree,
    staleTime: Infinity,
  });

  const { data: allProducts = [], isLoading } = useQuery({
    queryKey: ['shop-grid-all'],
    queryFn: () => shopService.getProducts({}),
    keepPreviousData: true,
  });

  /* ── فیلترینگ ── */
  const filteredProducts = useMemo(() => {
    let result = allProducts;

    if (selectedSlugs.length > 0 && categoriesTree.length > 0) {
      const selectedNames = [];
      const findNames = (list) => {
        list.forEach((cat) => {
          if (selectedSlugs.includes(cat.slug)) selectedNames.push(cat.name);
          if (cat.children) findNames(cat.children);
        });
      };
      findNames(categoriesTree);

      result = result.filter((product) => {
        if (!product.category) return false;
        const parentName = product.category.parent_category;
        const childName = product.category.children_category;
        return selectedNames.some((name) => name === parentName || name === childName);
      });
    }

    if (searchQuery) {
      result = result.filter((p) => p.name.includes(searchQuery));
    }

    return result;
  }, [allProducts, selectedSlugs, categoriesTree, searchQuery]);

  /* ── چیپس‌ها ── */
  const activeFilters = useMemo(() => {
    const names = [];
    const flatten = (cats) => {
      cats.forEach((c) => {
        if (selectedSlugs.includes(c.slug)) names.push({ name: c.name, slug: c.slug });
        if (c.children) flatten(c.children);
      });
    };
    flatten(categoriesTree);
    return names;
  }, [selectedSlugs, categoriesTree]);

  /* ── صفحه‌بندی ── */
  const { paginatedProducts, totalPages } = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    return {
      paginatedProducts: filteredProducts.slice(start, end),
      totalPages: Math.ceil(filteredProducts.length / ITEMS_PER_PAGE) || 1,
    };
  }, [filteredProducts, currentPage]);

  /* ── توابع ── */
  const removeFilter = useCallback(
    (slugToRemove) => {
      const newParams = new URLSearchParams(searchParams);
      newParams.delete('category');
      selectedSlugs
        .filter((s) => s !== slugToRemove)
        .forEach((s) => newParams.append('category', s));
      newParams.delete('page');
      setSearchParams(newParams);
    },
    [searchParams, selectedSlugs, setSearchParams]
  );

  const handleSearch = useCallback(
    (e) => {
      e.preventDefault();
      const newParams = new URLSearchParams(searchParams);
      if (localSearch.trim()) newParams.set('search', localSearch);
      else newParams.delete('search');
      newParams.delete('page');
      setSearchParams(newParams);
    },
    [localSearch, searchParams, setSearchParams]
  );

  const clearSearch = useCallback(() => {
    setLocalSearch('');
    const newParams = new URLSearchParams(searchParams);
    newParams.delete('search');
    newParams.delete('page');
    setSearchParams(newParams);
  }, [searchParams, setSearchParams]);

  const handlePageChange = useCallback(
    (page) => {
      const newParams = new URLSearchParams(searchParams);
      newParams.set('page', page);
      setSearchParams(newParams);
      // اسکرول نرم به بالای گرید
      gridRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },
    [searchParams, setSearchParams]
  );

  const totalFilters = activeFilters.length + (searchQuery ? 1 : 0);

  return (
    <div className="mx-auto px-4 md:px-6 py-6 md:py-8 max-w-[92vw]">

      {/* ════════════════ هدر موبایل ════════════════ */}
      <div className="flex lg:hidden justify-between items-center mb-5">
        <div>
          <h1 className="text-xl font-extrabold text-slate-800">
            {pageText.shop.shopTitle}
          </h1>
          {filteredProducts.length > 0 && (
            <p className="text-xs text-slate-400 font-medium mt-0.5">
              {filteredProducts.length} محصول
            </p>
          )}
        </div>
        <button
          onClick={() => setDrawerOpen(true)}
          className="
            relative flex items-center gap-2
            px-4 py-2.5 rounded-xl
            bg-white ring-1 ring-black/[0.06]
            text-sm font-bold text-slate-600
            hover:shadow-md hover:ring-black/[0.1]
            active:scale-[0.97]
            transition-all duration-200
          "
        >
          <Filter size={18} strokeWidth={2} />
          فیلتر
          {totalFilters > 0 && (
            <span className="
              absolute -top-1.5 -left-1.5
              w-5 h-5 flex items-center justify-center
              text-[10px] font-extrabold
              bg-primary text-white rounded-full
              shadow-sm shadow-primary/30
            ">
              {totalFilters}
            </span>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr] xl:grid-cols-[280px_1fr] gap-6 lg:gap-8">

        {/* ════════════════ سایدبار دسکتاپ ════════════════ */}
        <aside className="hidden lg:block">
          <div className="sticky top-24">
            <ShopSidebar />
          </div>
        </aside>

        {/* ════════════════ محتوای اصلی ════════════════ */}
        <main className="flex flex-col gap-5 min-w-0" ref={gridRef}>

          {/* ── جستجو + فیلترهای فعال ── */}
          <div className="
            bg-white rounded-2xl
            ring-1 ring-black/[0.04]
            shadow-sm
            overflow-hidden
          ">
            {/* فرم جستجو */}
            <form onSubmit={handleSearch} className="relative flex items-center p-3 md:p-4">
              <div className="
                relative flex-1 flex items-center
                bg-slate-50/80 rounded-xl
                ring-1 ring-slate-200/60
                focus-within:ring-2 focus-within:ring-primary/30 focus-within:bg-white
                transition-all duration-300
              ">
                <button
                  type="submit"
                  className="
                    absolute right-2.5
                    p-1.5 rounded-lg
                    text-slate-400 hover:text-primary hover:bg-primary/8
                    transition-colors duration-200
                  "
                >
                  <Search size={18} strokeWidth={2.2} />
                </button>
                <input
                  type="text"
                  placeholder={pageText.shop.searchPlaceholder}
                  className="
                    w-full py-2.5 px-4 pr-11
                    bg-transparent rounded-xl
                    text-right text-sm text-slate-700
                    placeholder:text-slate-400/70
                    focus:outline-none
                  "
                  value={localSearch}
                  onChange={(e) => setLocalSearch(e.target.value)}
                />
                <AnimatePresence>
                  {localSearch && (
                    <motion.button
                      type="button"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      onClick={() => {
                        setLocalSearch('');
                        // اگه قبلاً جستجو انجام شده بود پاکش کن
                        if (searchQuery) clearSearch();
                      }}
                      className="absolute left-2.5 p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                    >
                      <X size={14} />
                    </motion.button>
                  )}
                </AnimatePresence>
              </div>
            </form>

            {/* چیپس‌های فیلتر */}
            <AnimatePresence>
              {(activeFilters.length > 0 || searchQuery) && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.25 }}
                  className="overflow-hidden"
                >
                  <div className="flex flex-wrap items-center gap-2 px-4 pb-3.5 border-t border-slate-100/80 pt-3">
                    <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-400 ml-1">
                      <SlidersHorizontal size={13} />
                      {pageText.shop.filtersTitle}
                    </div>

                    {searchQuery && (
                      <motion.span
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="
                          inline-flex items-center gap-1.5
                          bg-primary/8 text-primary
                          pl-1.5 pr-3 py-1.5 rounded-lg
                          text-xs font-bold
                        "
                      >
                        <button
                          onClick={clearSearch}
                          className="p-0.5 rounded hover:bg-primary/15 transition-colors"
                        >
                          <X size={12} />
                        </button>
                        {pageText.shop.searchTitle} {searchQuery}
                      </motion.span>
                    )}

                    {activeFilters.map((f) => (
                      <motion.span
                        key={f.slug}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        layout
                        className="
                          inline-flex items-center gap-1.5
                          bg-slate-100 text-slate-600
                          pl-1.5 pr-3 py-1.5 rounded-lg
                          text-xs font-semibold
                          hover:bg-slate-200/80 transition-colors
                        "
                      >
                        <button
                          onClick={() => removeFilter(f.slug)}
                          className="p-0.5 rounded hover:bg-slate-300/60 text-slate-400 hover:text-slate-600 transition-colors"
                        >
                          <X size={12} />
                        </button>
                        {f.name}
                      </motion.span>
                    ))}

                    {activeFilters.length > 1 && (
                      <button
                        onClick={() => setSearchParams({})}
                        className="
                          mr-auto text-[11px] font-bold text-red-400 hover:text-red-500
                          px-2 py-1 rounded-md hover:bg-red-50
                          transition-colors
                        "
                      >
                        {pageText.shop.deleteAllFilters}
                      </button>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* ── نوار اطلاعات ── */}
          {!isLoading && filteredProducts.length > 0 && (
            <div className="hidden md:flex items-center justify-between px-1">
              <p className="text-[13px] text-slate-400 font-medium">
                <span className="font-extrabold text-slate-600">{filteredProducts.length}</span> محصول
                {totalPages > 1 && (
                  <span className="text-slate-300 mx-1.5">·</span>
                )}
                {totalPages > 1 && (
                  <span>
                    صفحه <span className="font-bold text-slate-500">{currentPage}</span> از {totalPages}
                  </span>
                )}
              </p>
            </div>
          )}

          {/* ── گرید محصولات ── */}
          {isLoading ? (
            <ProductGridSkeleton />
          ) : paginatedProducts.length > 0 ? (
            <>
              <motion.div
                variants={staggerGrid}
                initial="hidden"
                animate="show"
                key={`page-${currentPage}-${selectedSlugs.join('-')}-${searchQuery || ''}`}
                className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-5 min-h-[400px] content-start"
              >
                {paginatedProducts.map((product) => (
                  <motion.div
                    key={product.id}
                    variants={gridItemAnim}
                    layout
                    className="h-full"
                  >
                    <ProductCard product={product} />
                  </motion.div>
                ))}
              </motion.div>

              {/* پیجینیشن */}
              {totalPages > 1 && (
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={handlePageChange}
                />
              )}
            </>
          ) : (
            <EmptyState onReset={() => setSearchParams({})} />
          )}
        </main>
      </div>

      {/* ════════════════ دراور موبایل ════════════════ */}
      <AnimatePresence>
        {isDrawerOpen && (
          <MobileDrawer onClose={() => setDrawerOpen(false)}>
            <ShopSidebar closeMobileMenu={() => setDrawerOpen(false)} />
          </MobileDrawer>
        )}
      </AnimatePresence>
    </div>
  );
};

/* ═════════════════════════════════════════════
   پیجینیشن
   ═════════════════════════════════════════════ */
const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  // محاسبه صفحات قابل نمایش (حداکثر ۵ تا)
  const pages = useMemo(() => {
    const delta = 2;
    const range = [];
    const start = Math.max(1, currentPage - delta);
    const end = Math.min(totalPages, currentPage + delta);

    for (let i = start; i <= end; i++) range.push(i);

    // اضافه کردن ... اگه لازمه
    const result = [];
    if (range[0] > 1) {
      result.push(1);
      if (range[0] > 2) result.push('...');
    }
    result.push(...range);
    if (range[range.length - 1] < totalPages) {
      if (range[range.length - 1] < totalPages - 1) result.push('...');
      result.push(totalPages);
    }
    return result;
  }, [currentPage, totalPages]);

  return (
    <div className="flex justify-center mt-6 dir-ltr">
      <div className="
        inline-flex items-center gap-1
        bg-white rounded-2xl
        ring-1 ring-black/[0.05]
        shadow-sm
        p-1.5
      ">
        {/* قبلی */}
        <button
          disabled={currentPage === 1}
          onClick={() => onPageChange(currentPage - 1)}
          className="
            w-9 h-9 flex items-center justify-center rounded-xl
            text-slate-400 hover:text-slate-600 hover:bg-slate-100
            disabled:opacity-30 disabled:cursor-not-allowed
            transition-all duration-200
          "
        >
          <ChevronRight size={18} />
        </button>

        {/* شماره‌ها */}
        {pages.map((page, idx) =>
          page === '...' ? (
            <span key={`dots-${idx}`} className="w-9 h-9 flex items-center justify-center text-slate-300 text-sm">
              ···
            </span>
          ) : (
            <button
              key={page}
              onClick={() => onPageChange(page)}
              className={clsx(
                'w-9 h-9 flex items-center justify-center rounded-xl text-sm font-bold transition-all duration-200',
                currentPage === page
                  ? 'bg-primary text-white shadow-md shadow-primary/25'
                  : 'text-slate-500 hover:bg-slate-100 hover:text-slate-700'
              )}
            >
              {page}
            </button>
          )
        )}

        {/* بعدی */}
        <button
          disabled={currentPage === totalPages}
          onClick={() => onPageChange(currentPage + 1)}
          className="
            w-9 h-9 flex items-center justify-center rounded-xl
            text-slate-400 hover:text-slate-600 hover:bg-slate-100
            disabled:opacity-30 disabled:cursor-not-allowed
            transition-all duration-200
          "
        >
          <ChevronLeft size={18} />
        </button>
      </div>
    </div>
  );
};

/* ═════════════════════════════════════════════
   حالت خالی
   ═════════════════════════════════════════════ */
const EmptyState = ({ onReset }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4 }}
    className="
      flex flex-col items-center justify-center
      py-20 md:py-28
      bg-white rounded-3xl
      ring-1 ring-black/[0.04]
      shadow-sm
    "
  >
    <div className="
      w-20 h-20 rounded-3xl
      bg-gradient-to-br from-slate-100 to-slate-50
      flex items-center justify-center mb-5
      ring-1 ring-black/[0.03]
    ">
      <PackageOpen size={36} strokeWidth={1.3} className="text-slate-300" />
    </div>
    <h3 className="text-lg font-extrabold text-slate-700 mb-1.5">
      {pageText.shop.productNotFound}
    </h3>
    <p className="text-sm text-slate-400 font-medium mb-6">
      فیلترها رو تغییر بدید یا همه محصولات رو ببینید
    </p>
    <button
      onClick={onReset}
      className="
        inline-flex items-center gap-2
        px-6 py-2.5 rounded-xl
        bg-primary text-white text-sm font-bold
        shadow-md shadow-primary/20
        hover:shadow-lg hover:shadow-primary/30
        hover:-translate-y-[1px]
        active:translate-y-0
        transition-all duration-200
      "
    >
      <Sparkles size={15} />
      {pageText.shop.allProductsTitle}
    </button>
  </motion.div>
);

/* ═════════════════════════════════════════════
   اسکلتون گرید
   ═════════════════════════════════════════════ */
const shimmer =
  'relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_1.8s_infinite] before:bg-gradient-to-r before:from-transparent before:via-white/50 before:to-transparent';

const ProductGridSkeleton = () => (
  <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-5">
    {[...Array(6)].map((_, i) => (
      <div
        key={i}
        className="bg-white rounded-2xl ring-1 ring-black/[0.04] overflow-hidden"
        style={{ animationDelay: `${i * 100}ms` }}
      >
        <div className={`h-48 bg-slate-100 ${shimmer}`} />
        <div className="p-4 space-y-3">
          <div className={`h-4 w-3/4 bg-slate-100 rounded-lg ${shimmer}`} />
          <div className={`h-3 w-1/2 bg-slate-50 rounded-lg ${shimmer}`} />
          <div className="flex justify-between items-center pt-2">
            <div className={`h-5 w-24 bg-slate-100 rounded-lg ${shimmer}`} />
            <div className={`h-8 w-8 bg-slate-100 rounded-lg ${shimmer}`} />
          </div>
        </div>
      </div>
    ))}
  </div>
);

/* ═════════════════════════════════════════════
   دراور موبایل
   ═════════════════════════════════════════════ */
const MobileDrawer = ({ onClose, children }) => (
  <div className="fixed inset-0 z-[60] lg:hidden">
    {/* اورلی */}
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.25 }}
      className="absolute inset-0 bg-black/40 backdrop-blur-sm"
      onClick={onClose}
    />
    {/* پنل */}
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="
        absolute inset-y-0 right-0 w-[300px]
        bg-white/[0.98] backdrop-blur-xl
        shadow-[−20px_0_60px_−10px_rgba(0,0,0,0.1)]
        flex flex-col
      "
    >
      {/* هدر دراور */}
      <div className="flex items-center justify-between px-4 py-3.5 border-b border-slate-100">
        <h3 className="text-sm font-extrabold text-slate-700 flex items-center gap-2">
          <SlidersHorizontal size={16} className="text-primary" />
          فیلتر محصولات
        </h3>
        <button
          onClick={onClose}
          className="
            w-8 h-8 flex items-center justify-center
            rounded-lg text-slate-400 hover:text-slate-600
            hover:bg-slate-100 transition-colors
          "
        >
          <X size={18} />
        </button>
      </div>

      {/* محتوا */}
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        {children}
      </div>
    </motion.div>
  </div>
);

export default ShopPage;