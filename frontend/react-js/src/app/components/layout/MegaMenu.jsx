// src/app/components/layout/MegaMenu.jsx
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { ChevronLeft, ArrowLeft, Image as ImageIcon } from 'lucide-react';
import { categoryService } from '../../services/categoryService';

const MegaMenu = ({ isOpen }) => {
  const [activeId, setActiveId] = useState(null);
  const [hasOpenedOnce, setHasOpenedOnce] = useState(false);

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

  if (!hasOpenedOnce && !categories) return null;

  const activeCategory = categories?.find(c => c.id === activeId) || categories?.[0];

  return (
    // ارتفاع کمتر (450px) برای جمع‌وجور شدن کل منو
    <div className="w-full bg-white shadow-xl rounded-b-xl border-t border-base-200 overflow-hidden flex h-[70vh]">
      
      {isLoading ? (
        <MegaMenuSkeleton />
      ) : (
        <>
          {/* --- سایدبار فشرده و لیست‌وار --- */}
          <div className="w-[220px] flex-shrink-0 bg-gray-50/80 border-l border-gray-100 py-3 overflow-y-auto custom-scrollbar">
            <ul className="space-y-0 px-2">
              {categories?.map((cat) => (
                <li key={cat.id}>
                  <button
                    onMouseEnter={() => setActiveId(cat.id)}
                    className={`
                      w-full flex items-center justify-between px-3 py-2.5 rounded-md text-xs md:text-sm transition-all duration-200
                      ${activeId === cat.id 
                        ? 'bg-primary text-white font-bold shadow-sm ring-1 ring-gray-100' 
                        : 'text-gray-500 hover:bg-gray-100 font-medium'
                      }
                    `}
                  >
                    <span className="truncate">{cat.name}</span>
                    {activeId === cat.id && <ChevronLeft size={14} className="text-white" />}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* --- بدنه اصلی: گرید متراکم (Compact Grid) --- */}
          <div className="flex-1 p-6 bg-white overflow-y-auto custom-scrollbar">
            
            {activeCategory && (
              <div className="animate-in fade-in duration-200">
                
                {/* هدر کوچک شده */}
                <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-2">
                  <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                    <span className="w-1 h-5 bg-primary rounded-full"></span>
                    {activeCategory.name}
                  </h3>
                  <Link 
                    to={`/category/${activeCategory.slug}`} 
                    className="text-xs font-bold text-primary hover:bg-primary/5 px-2 py-1 rounded transition-colors flex items-center gap-1"
                  >
                    مشاهده همه
                    <ArrowLeft size={14} />
                  </Link>
                </div>

                {/* نکته کلیدی: گرید ۶ یا ۷ ستونه برای کوچک شدن عکس‌ها 
                   gap-3 برای نزدیک‌تر شدن آیتم‌ها
                */}
                {activeCategory.children?.length > 0 ? (
                  <div className="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-7 gap-3">
                    {activeCategory.children.map((sub) => (
                      <Link 
                        key={sub.id} 
                        to={`/category/${activeCategory.slug}/${sub.slug}`}
                        className="group flex flex-col items-center gap-2 p-2 rounded-lg hover:bg-gray-50 transition-colors border border-transparent hover:border-gray-100"
                      >
                        {/* کانتینر تصویر: سایز عکس الان توسط تعداد ستون‌ها کنترل میشه و ریزتره */}
                        <div className="relative aspect-square w-full overflow-hidden rounded-lg bg-white border border-gray-100 group-hover:border-primary/30 shadow-sm transition-all">
                          {sub.thumbnail ? (
                            <img 
                              src={sub.thumbnail} 
                              alt={sub.name} 
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" 
                            />
                          ) : (
                            <div className="absolute inset-0 flex items-center justify-center text-gray-300">
                              <ImageIcon size={20} />
                            </div>
                          )}
                        </div>
                        
                        {/* متن: فونت ریزتر برای تناسب با عکس */}
                        <span className="text-xs font-medium text-center text-gray-600 group-hover:text-primary line-clamp-2 h-8 leading-4 flex items-center justify-center">
                          {sub.name}
                        </span>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-48 text-gray-300 text-sm">
                    <p>بدون زیرمجموعه</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

const MegaMenuSkeleton = () => (
    <div className="flex w-full h-full animate-pulse bg-white">
        <div className="w-[220px] bg-gray-50 border-l p-3 space-y-2">
            {[...Array(12)].map((_,i) => <div key={i} className="h-8 bg-gray-200 rounded"></div>)}
        </div>
        <div className="flex-1 p-6 space-y-4">
            <div className="h-6 w-32 bg-gray-200 rounded"></div>
            <div className="grid grid-cols-6 gap-3">
                {[...Array(18)].map((_,i) => (
                   <div key={i} className="aspect-square bg-gray-100 rounded-lg"></div>
                ))}
            </div>
        </div>
    </div>
);

export default MegaMenu;