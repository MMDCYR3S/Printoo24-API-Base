import { useState, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { shopService } from '../../services/shopService';
import { categoryService } from '../../services/categoryService';
import ProductCard from '../../components/product/ProductCard';
import ShopSidebar from './components/ShopSidebar';
import { Search, Filter, X, ChevronLeft, ChevronRight, SlidersHorizontal } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import clsx from 'clsx'; // باگ clsx رفع شد
import pageText from '../../lang/pages.json'

const ITEMS_PER_PAGE = 12;

const ShopPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [localSearch, setLocalSearch] = useState(searchParams.get('search') || '');

  // پارامترهای URL
  const selectedSlugs = searchParams.getAll('category'); // اسلاگ‌های انتخاب شده (انگلیسی)
  const searchQuery = searchParams.get('search');
  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  // ۱. دریافت درخت دسته‌بندی‌ها (برای پیدا کردن نام فارسی از روی اسلاگ)
  const { data: categoriesTree = [] } = useQuery({
    queryKey: ['categories-tree'],
    queryFn: categoryService.getCategoriesTree,
    staleTime: Infinity,
  });

  // ۲. دریافت همه محصولات (بدون فیلتر سروری، چون سرور همه را می‌دهد)
  const { data: allProducts = [], isLoading } = useQuery({
    queryKey: ['shop-grid-all'], 
    queryFn: () => shopService.getProducts({}), // درخواست بدون فیلتر به سرور
    keepPreviousData: true,
  });

  // ۳. لاجیک فیلترینگ سمت کلاینت (Front-end Filtering)
  const filteredProducts = useMemo(() => {
    let result = allProducts;

    // الف) فیلتر بر اساس دسته‌بندی
    if (selectedSlugs.length > 0 && categoriesTree.length > 0) {
      // گام اول: پیدا کردن نام‌های فارسی مرتبط با اسلاگ‌های انتخاب شده
      const selectedNames = [];
      const findNames = (list) => {
        list.forEach(cat => {
          if (selectedSlugs.includes(cat.slug)) {
            selectedNames.push(cat.name);
          }
          if (cat.children) findNames(cat.children);
        });
      };
      findNames(categoriesTree);

      // گام دوم: فیلتر کردن محصولات
      result = result.filter(product => {
        // اگر محصول اصلا دسته ندارد، حذف شود
        if (!product.category) return false;

        // بررسی تطابق با دسته مادر یا زیردسته
        const parentName = product.category.parent_category;
        const childName = product.category.children_category;

        return selectedNames.some(name => name === parentName || name === childName);
      });
    }

    // ب) فیلتر جستجو (Search)
    if (searchQuery) {
      result = result.filter(p => p.name.includes(searchQuery));
    }

    return result;
  }, [allProducts, selectedSlugs, categoriesTree, searchQuery]);

  // ۴. لاجیک چیپس‌های فیلتر فعال (برای نمایش بالای گرید)
  const activeFilters = useMemo(() => {
    const names = [];
    const flattenCategories = (cats) => {
      cats.forEach(c => {
        if (selectedSlugs.includes(c.slug)) names.push({ name: c.name, slug: c.slug });
        if (c.children) flattenCategories(c.children);
      });
    };
    flattenCategories(categoriesTree);
    return names;
  }, [selectedSlugs, categoriesTree]);

  // ۵. صفحه‌بندی (Pagination) روی نتایج فیلتر شده
  const { paginatedProducts, totalPages } = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    return {
      paginatedProducts: filteredProducts.slice(start, end),
      totalPages: Math.ceil(filteredProducts.length / ITEMS_PER_PAGE) || 1
    };
  }, [filteredProducts, currentPage]);

  // توابع کمکی
  const removeFilter = (slugToRemove) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.delete('category');
    selectedSlugs.filter(s => s !== slugToRemove).forEach(s => newParams.append('category', s));
    newParams.delete('page');
    setSearchParams(newParams);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    const newParams = new URLSearchParams(searchParams);
    if (localSearch.trim()) newParams.set('search', localSearch);
    else newParams.delete('search');
    newParams.delete('page');
    setSearchParams(newParams);
  };

  const handlePageChange = (page) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', page);
    setSearchParams(newParams);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* هدر موبایل */}
      <div className="flex lg:hidden justify-between items-center mb-4">
        <h1 className="text-xl font-bold text-slate-800">{pageText.shop.shopTitle}</h1>
        <button className="btn btn-square btn-ghost" onClick={() => setDrawerOpen(true)}>
          <Filter size={24} />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* سایدبار */}
        <div className="hidden lg:block lg:col-span-1">
          <ShopSidebar />
        </div>

        {/* محتوای اصلی */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          
          {/* باکس جستجو و چیپس‌ها */}
          <div className="bg-white p-4 rounded-[24px] border border-slate-100 shadow-sm">
            <form onSubmit={handleSearch} className="relative flex items-center">
              <input 
                type="text" 
                placeholder={pageText.shop.searchPlaceholder} 
                className="input input-bordered w-full pr-12 rounded-xl focus:outline-none focus:border-primary bg-slate-50"
                value={localSearch}
                onChange={(e) => setLocalSearch(e.target.value)}
              />
              <button type="submit" className="absolute right-3 text-slate-400 hover:text-primary transition-colors">
                <Search size={22} />
              </button>
            </form>

            {(activeFilters.length > 0 || searchQuery) && (
              <div className="flex flex-wrap gap-2 mt-4 pt-3 border-t border-slate-50">
                <div className="flex items-center gap-2 text-xs font-bold text-slate-400 ml-2">
                   <SlidersHorizontal size={14} />
                   {pageText.shop.filtersTitle}
                </div>
                {searchQuery && (
                   <div className="badge badge-lg gap-2 bg-primary/10 text-primary border-0 rounded-lg pl-1 pr-3">
                     <span className="text-xs">{pageText.shop.searchTitle} {searchQuery}</span>
                     <button onClick={() => { setLocalSearch(''); handleSearch({ preventDefault: ()=>{} }); }} className="hover:bg-primary/20 rounded-full p-0.5"><X size={14} /></button>
                   </div>
                )}
                {activeFilters.map((f) => (
                  <div key={f.slug} className="badge badge-lg gap-2 bg-slate-100 text-slate-700 border-0 rounded-lg pl-1 pr-3 hover:bg-slate-200 transition-colors">
                    <span className="text-xs">{f.name}</span>
                    <button onClick={() => removeFilter(f.slug)} className="hover:bg-slate-300 rounded-full p-0.5 text-slate-500"><X size={14} /></button>
                  </div>
                ))}
                {(activeFilters.length > 1) && (
                  <button onClick={() => setSearchParams({})} className="text-xs text-red-500 hover:underline mr-auto font-medium">{pageText.shop.deleteAllFilters}</button>
                )}
              </div>
            )}
          </div>

          {/* گرید محصولات */}
          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="flex flex-col gap-3">
                   <div className="skeleton h-48 w-full rounded-[24px]"></div>
                   <div className="skeleton h-4 w-2/3 rounded-lg"></div>
                </div>
              ))}
            </div>
          ) : paginatedProducts.length > 0 ? (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6 min-h-[400px] content-start">
                <AnimatePresence mode="popLayout">
                  {paginatedProducts.map((product) => (
                    <motion.div
                      key={product.id}
                      layout
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      transition={{ duration: 0.2 }}
                      className="h-full"
                    >
                      <ProductCard product={product} /> 
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>

              {/* پیجینیشن */}
              {totalPages > 1 && (
                <div className="flex justify-center mt-8 dir-ltr">
                  <div className="join bg-white border border-slate-100 rounded-2xl shadow-sm p-1">
                    <button className="join-item btn btn-sm btn-ghost" disabled={currentPage === 1} onClick={() => handlePageChange(currentPage - 1)}>
                      <ChevronRight size={16} />
                    </button>
                    {[...Array(totalPages)].map((_, i) => (
                       <button key={i} className={clsx("join-item btn btn-sm border-0", currentPage === i + 1 ? "btn-primary text-white shadow-md rounded-lg" : "btn-ghost text-slate-500")} onClick={() => handlePageChange(i + 1)}>{i + 1}</button>
                    ))}
                    <button className="join-item btn btn-sm btn-ghost" disabled={currentPage === totalPages} onClick={() => handlePageChange(currentPage + 1)}>
                      <ChevronLeft size={16} />
                    </button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="flex flex-col items-center justify-center py-20 bg-white rounded-[32px] border border-slate-100 shadow-sm text-center">
              <div className="bg-slate-50 p-6 rounded-full mb-4">
                <Search className="w-12 h-12 text-slate-300" />
              </div>
              <h3 className="text-xl font-bold text-slate-700">{pageText.shop.productNotFound}</h3>
              <button onClick={() => setSearchParams({})} className="btn btn-primary btn-sm mt-6 rounded-full px-6">{pageText.shop.allProductsTitle}</button>
            </div>
          )}
        </div>
      </div>

      {isDrawerOpen && (
        <div className="fixed inset-0 z-[60] lg:hidden">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setDrawerOpen(false)}></div>
          <div className="absolute inset-y-0 right-0 w-80 bg-white shadow-2xl p-4 overflow-y-auto">
            <ShopSidebar closeMobileMenu={() => setDrawerOpen(false)} />
          </div>
        </div>
      )}
    </div>
  );
};

export default ShopPage;