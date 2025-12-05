// src/app/components/layout/MegaMenu.jsx
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { ChevronLeft, ImageOff } from 'lucide-react';
import { categoryService } from '../../services/categoryService';

const MegaMenu = () => {
  const [activeId, setActiveId] = useState(null);

  // 1. دریافت اطلاعات از سرور با کشینگ
  const { data: categories, isLoading, isError } = useQuery({
    queryKey: ['categories-tree'],
    queryFn: categoryService.getCategoriesTree,
    staleTime: 1000 * 60 * 60, // 1 ساعت کش بماند (منو دیر به دیر عوض می‌شود)
  });

  // وقتی دیتا آمد، اولین دسته را پیش‌فرض انتخاب کن
  useEffect(() => {
    if (categories && categories.length > 0 && !activeId) {
      setActiveId(categories[0].id);
    }
  }, [categories, activeId]);

  // هندل کردن لودینگ (نمایش اسکلتون برای حس سرعت)
  if (isLoading) return <MegaMenuSkeleton />;
  if (isError) return <div className="p-4 text-error">خطا در بارگذاری منو</div>;

  // پیدا کردن دسته فعال
  const activeCategory = categories.find(c => c.id === activeId) || categories[0];

  return (
    <div className="container mx-auto flex h-[500px] bg-base-100 shadow-xl rounded-b-box overflow-hidden border-t border-base-200">
      
      {/* ستون راست: دسته‌بندی‌های اصلی (لیست) */}
      <div className="w-1/4 max-w-[280px] bg-base-200/50 overflow-y-auto custom-scrollbar border-l border-base-300">
        <ul className="py-2">
          {categories.map((cat) => (
            <li key={cat.id}>
              <div
                onMouseEnter={() => setActiveId(cat.id)}
                className={`
                  flex items-center justify-between px-4 py-3 cursor-pointer transition-all duration-200
                  ${activeId === cat.id 
                    ? 'bg-white text-primary font-black border-r-4 border-primary shadow-sm' 
                    : 'text-base-content/70 hover:bg-base-200 hover:text-base-content hover:pr-5 border-r-4 border-transparent'
                  }
                `}
              >
                <span className="text-sm md:text-base">{cat.name}</span>
                {activeId === cat.id && <ChevronLeft size={16} className="text-primary" />}
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* ستون چپ: زیردسته‌ها (گرید تصویری) */}
      <div className="flex-1 p-6 overflow-y-auto bg-white custom-scrollbar">
        {/* هدر بخش چپ */}
        <div className="flex items-center justify-between mb-6 border-b border-base-100 pb-4">
          <h3 className="text-2xl font-black text-base-content flex items-center gap-2">
            <span className="w-3 h-8 bg-secondary rounded-full inline-block"></span>
            {activeCategory.name}
          </h3>
          <Link 
            to={`/category/${activeCategory.slug}`} 
            className="btn btn-ghost btn-sm text-primary font-bold hover:bg-primary/10"
          >
            مشاهده همه محصولات
            <ChevronLeft size={16} />
          </Link>
        </div>

        {/* گرید زیردسته‌ها */}
        {activeCategory.children && activeCategory.children.length > 0 ? (
          <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {activeCategory.children.map((sub) => (
              <Link 
                key={sub.id} 
                to={`/category/${activeCategory.slug}/${sub.slug}`}
                className="group flex flex-col items-center text-center p-2 rounded-xl hover:bg-base-200/50 transition-colors"
              >
                {/* تصویر ۱:۱ با گوشه‌های گرد */}
                <div className="relative aspect-square w-full mb-3 overflow-hidden rounded-2xl border border-base-200 shadow-sm group-hover:shadow-md group-hover:border-primary/30 transition-all bg-base-100">
                  {sub.thumbnail ? (
                    <img 
                      src={sub.thumbnail} 
                      alt={sub.name}
                      loading="lazy"
                      className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-500"
                      onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }}
                    />
                  ) : null}
                  {/* فال‌بک اگر عکس لود نشد */}
                  <div className="absolute inset-0 flex items-center justify-center bg-base-200 text-base-content/20" style={{display: sub.thumbnail ? 'none' : 'flex'}}>
                    <ImageOff size={24} />
                  </div>
                </div>
                
                {/* نام زیردسته */}
                <span className="text-sm font-bold text-base-content/80 group-hover:text-primary leading-tight">
                  {sub.name}
                </span>
              </Link>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 text-base-content/40">
            <p>هیچ زیردسته‌ای یافت نشد.</p>
          </div>
        )}
      </div>
    </div>
  );
};

// کامپوننت لودینگ (Skeleton) برای UX بهتر
const MegaMenuSkeleton = () => (
  <div className="container mx-auto flex h-[500px] bg-base-100 shadow-xl rounded-b-box border-t border-base-200">
    <div className="w-1/4 bg-base-200/50 p-2 space-y-2">
      {[...Array(8)].map((_, i) => (
        <div key={i} className="h-10 bg-base-300 rounded w-full animate-pulse"></div>
      ))}
    </div>
    <div className="flex-1 p-6">
      <div className="h-8 w-48 bg-base-300 rounded mb-6 animate-pulse"></div>
      <div className="grid grid-cols-4 gap-4">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="aspect-square bg-base-300 rounded-2xl animate-pulse"></div>
        ))}
      </div>
    </div>
  </div>
);

export default MegaMenu;