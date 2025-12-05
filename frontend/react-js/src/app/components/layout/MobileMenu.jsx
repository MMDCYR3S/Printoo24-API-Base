// src/app/components/layout/MobileMenu.jsx
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { categoryService } from '../../services/categoryService';

const MobileMenu = ({ onClose }) => {
  const { data: categories } = useQuery({
    queryKey: ['categories-tree'],
    queryFn: categoryService.getCategoriesTree,
    staleTime: 1000 * 60 * 60,
  });

  if (!categories) return <div className="p-4 text-center loading loading-dots"></div>;

  return (
    <div className="flex flex-col w-full">
      {categories.map((cat) => (
        <div key={cat.id} className="collapse collapse-arrow border-b border-base-200 rounded-none bg-base-100">
          <input type="radio" name="mobile-accordion" /> 
          
          {/* عنوان دسته اصلی */}
          <div className="collapse-title text-base font-bold text-base-content/90 py-4 min-h-0 flex items-center">
            {cat.name}
          </div>
          
          {/* لیست زیردسته‌ها */}
          <div className="collapse-content px-0"> 
            <ul className="menu menu-sm bg-base-100 w-full p-0">
              {/* لینک "همه موارد" برای خود دسته اصلی */}
              <li>
                <Link 
                  to={`/category/${cat.slug}`} 
                  onClick={onClose}
                  className="pl-8 py-3 text-primary font-bold border-r-[3px] border-primary/20 hover:bg-base-200"
                >
                  همه محصولات {cat.name}
                </Link>
              </li>
              
              {/* زیردسته‌ها */}
              {cat.children?.map((sub) => (
                <li key={sub.id}>
                  <Link 
                    to={`/category/${cat.slug}/${sub.slug}`}
                    onClick={onClose}
                    className="pl-8 py-3 text-base-content/70 border-r-[3px] border-transparent hover:border-base-300"
                  >
                    {sub.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MobileMenu;