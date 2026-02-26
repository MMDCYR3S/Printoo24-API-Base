import React from 'react';
import { FileQuestion, AlertCircle } from 'lucide-react';
import SEO from '../../../components/common/SEO';
import BlogSidebar from '../components/BlogSidebar';
import ArticleCard from '../components/ArticleCard';
import Pagination from '../components/Pagination';
import { useBlog } from '../hooks/useBlog';
import { Search } from 'lucide-react'
import Top from '../../../../assets/top.svg'

const ArticleSkeleton = () => (
  <div className="bg-white rounded-2xl overflow-hidden border border-slate-100 shadow-sm flex flex-col h-full animate-pulse">
    <div className="aspect-[16/9] bg-slate-200 w-full" />
    <div className="p-5 flex flex-col flex-1 gap-4">
      <div className="h-6 bg-slate-200 rounded-md w-3/4" />
      <div className="space-y-2 flex-1">
        <div className="h-4 bg-slate-200 rounded w-full" />
        <div className="h-4 bg-slate-200 rounded w-5/6" />
      </div>
    </div>
  </div>
);

const BlogListPage = () => {
  const {
    articles,
    categories,
    isLoading,
    error,
    filters,
    handleFilterChange,
  } = useBlog();

  // فرض می‌کنیم اگر تعداد مقالات دریافتی در این صفحه کمتر از 10 تا بود، صفحه بعدی وجود ندارد
  // (این منطق بسته به ساختار دقیق response بک‌اند شما باید تنظیم شود)
  const hasMore = articles.length >= 10; 

  return (
    <div className="">
      <SEO 
        title="Blog & Articles" 
        description="Stay updated with the latest printing technologies, design tips, and news from Printoo24."
      />

      {/* ── هدر صفحه ── */}


      <div style={{ backgroundImage: `url(${Top})` , backgroundSize: "cover" , backgroundPosition: "center" }}  className="mb-8   bg-contain h-50 bg-no-repeat md:h-80 -mt-8 w-screen flex flex-row items-center">
  <div className='w-full max-w-[90vw]  mx-auto'>
    

    <div className='bg-radial from-secondary/40 to-primary/30 backdrop-blur-xs inset-shadow-xs inline-block p-4 rounded-2xl'>
        <div className='text-primary text-5xl md:text-6xl flex flex-col font-extrabold '>
            <span className='z-10 text-shadow-lg '>
            بلاگ‌ها
            </span>


            <span className='text-white text-stroke border-slate-500  font-extrabold text-4xl -mt-7 -ml-1 md:text-5xl text-left '>
                 Blogs
            </span>

        </div>

    </div>
    
  </div>
</div>

      <div className='max-w-[90vw] mx-auto'>
            {/* ── بخش جستجو ── */}
      <div className=" my-8 bg-radial from-white -mt-20 to-slate-100 p-5 rounded-2xl border border-slate-100 ">
        <div className="relative">
          <input
            type="text"
            placeholder="Search articles..."
            defaultValue={filters.searchQuery}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                onFilterChange('search', e.target.value);
              }
            }}
            className="w-full inset-shadow-slate-200 inset-shadow-sm bg-slate-50 border border-slate-200 text-slate-700 text-sm rounded-xl pl-10 pr-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
          />
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-primary" />
        </div>
        <p className="text-[11px] text-primary mt-2 px-1 ">Press Enter to search</p>
      </div>

      {/* ── ساختار دو ستونه (سایدبار + لیست مقالات) ── */}
      <div className="flex flex-col lg:flex-row gap-8 items-start">
        
        {/* ستون کناری: فیلترها و جستجو */}
        <BlogSidebar 
          categories={categories}
          filters={filters}
          onFilterChange={handleFilterChange}
        />

        {/* ستون اصلی: لیست مقالات */}
        <div className="flex-1 w-full">
          
          {error && (
            <div className="bg-red-50 border border-red-100 text-red-600 p-6 rounded-2xl flex items-center justify-center gap-3 mb-6">
              <AlertCircle size={24} />
              <p className="font-medium">{error}</p>
            </div>
          )}

          {!error && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {isLoading ? (
                  Array.from({ length: 4 }).map((_, idx) => <ArticleSkeleton key={idx} />)
                ) : articles.length > 0 ? (
                  articles.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))
                ) : (
                  <div className="col-span-full py-20 flex flex-col items-center justify-center text-center bg-slate-50 rounded-3xl border border-slate-200 border-dashed">
                    <FileQuestion size={48} className="text-slate-300 mb-4" />
                    <h3 className="text-lg font-bold text-slate-700 mb-2">No Articles Found</h3>
                    <p className="text-slate-500 text-sm max-w-sm">
                      We couldn't find any articles matching your search or filters. Try adjusting them.
                    </p>
                    <button 
                      onClick={() => {
                        handleFilterChange('search', null);
                        handleFilterChange('category', null);
                      }}
                      className="mt-6 px-6 py-2 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary/90 transition-all"
                    >
                      Clear All Filters
                    </button>
                  </div>
                )}
              </div>

              {/* پجینیشن (فقط وقتی دیتایی هست یا لودینگ تمام شده نشونش میدیم) */}
              {!isLoading && articles.length > 0 && (
                <Pagination 
                  currentPage={filters.page}
                  onPageChange={(newPage) => handleFilterChange('page', newPage.toString())}
                  hasMore={hasMore}
                />
              )}
            </>
          )}

        </div>
      </div>
    </div>
    </div>
  );
};

export default BlogListPage;