import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { categoryService } from '../../../services/categoryService';
import { FolderOpen, ChevronDown, Check } from 'lucide-react';
import clsx from 'clsx';

const ShopSidebar = ({ className, closeMobileMenu }) => {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // دریافت همه دسته‌های انتخاب شده به صورت آرایه
  const selectedCategories = searchParams.getAll('category');

  const { data: categories = [], isLoading } = useQuery({
    queryKey: ['categories-tree'],
    queryFn: categoryService.getCategoriesTree,
    staleTime: 1000 * 60 * 60,
  });

  const [expandedIds, setExpandedIds] = useState([]);

  // باز کردن خودکار والد دسته‌های انتخاب شده
  useEffect(() => {
    if (categories.length > 0 && selectedCategories.length > 0) {
      const parentsToExpand = categories
        .filter(p => selectedCategories.some(slug => 
          p.slug === slug || p.children?.some(c => c.slug === slug)
        ))
        .map(p => p.id);
      
      setExpandedIds(prev => [...new Set([...prev, ...parentsToExpand])]);
    }
  }, [categories, selectedCategories.length]);

  // هندل کردن تغییر چک‌باکس
  const handleCheckboxChange = (slug) => {
    const newParams = new URLSearchParams(searchParams);
    const currentSelected = newParams.getAll('category');
    
    if (currentSelected.includes(slug)) {
      // حذف اگر قبلا بوده
      newParams.delete('category');
      currentSelected.filter(s => s !== slug).forEach(s => newParams.append('category', s));
    } else {
      // اضافه کردن
      newParams.append('category', slug);
    }

    // ریست کردن پیجینیشن وقتی فیلتر عوض میشه
    newParams.delete('page'); 
    
    setSearchParams(newParams);
  };

  const toggleExpand = (id) => {
    setExpandedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  if (isLoading) return <div className="skeleton h-96 w-full rounded-2xl opacity-50"></div>;

  return (
    <aside className={clsx("bg-white p-5 rounded-[24px] border border-slate-100 h-fit w-full shadow-sm", className)}>
      <div className="flex items-center justify-between mb-5 pb-3 border-b border-slate-100">
        <h3 className="font-bold text-lg flex items-center gap-2 text-slate-800">
          <FolderOpen className="text-primary w-5 h-5" />
          دسته‌بندی‌ها
        </h3>
      </div>

      <ul className="flex flex-col gap-2">
        {categories.map((parent) => {
          const isExpanded = expandedIds.includes(parent.id);
          const isParentSelected = selectedCategories.includes(parent.slug);

          return (
            <li key={parent.id} className="collapse collapse-arrow bg-slate-50 rounded-xl border border-transparent hover:border-slate-200 transition-all">
              <input 
                type="checkbox" 
                className="peer min-h-0"
                checked={isExpanded}
                onChange={() => toggleExpand(parent.id)}
              />
              
              <div className="collapse-title min-h-0 py-3 px-4 flex items-center gap-3">
                {/* چک باکس والد */}
                <input 
                  type="checkbox"
                  className="checkbox checkbox-primary checkbox-sm rounded-md z-10"
                  checked={isParentSelected}
                  onChange={(e) => {
                    e.stopPropagation(); // جلوگیری از بسته شدن آکاردئون
                    handleCheckboxChange(parent.slug);
                  }}
                />
                <span className={clsx("font-bold text-sm select-none", isParentSelected ? "text-primary" : "text-slate-600")}>
                  {parent.name}
                </span>
              </div>

              <div className="collapse-content px-0 peer-checked:bg-white peer-checked:pb-2">
                {parent.children && parent.children.length > 0 && (
                  <ul className="w-full pt-2 px-4 gap-1 flex flex-col border-t border-slate-100">
                    {parent.children.map((child) => {
                      const isChildSelected = selectedCategories.includes(child.slug);
                      
                      return (
                        <li key={child.id} className="form-control">
                          <label className="label cursor-pointer py-2 justify-start gap-3 hover:bg-slate-50 rounded-lg px-2 transition-colors">
                            <input 
                              type="checkbox" 
                              className="checkbox checkbox-xs checkbox-primary rounded-sm"
                              checked={isChildSelected}
                              onChange={() => handleCheckboxChange(child.slug)}
                            />
                            <span className={clsx("text-sm", isChildSelected ? "text-slate-900 font-bold" : "text-slate-500")}>
                              {child.name}
                            </span>
                          </label>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </aside>
  );
};

export default ShopSidebar;