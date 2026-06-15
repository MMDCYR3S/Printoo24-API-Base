// src/app/components/layout/MobileMenu.jsx
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { categoryService } from "../../services/categoryService";
import {
  ChevronDownIcon,
  Squares2X2Icon,
  ChevronLeftIcon,
} from "@heroicons/react/24/outline";

const MobileMenu = ({ onClose }) => {
  const [expandedId, setExpandedId] = useState(null);

  const { data: categories, isLoading } = useQuery({
    queryKey: ["categories-tree"],
    queryFn: categoryService.getCategoriesTree,
    staleTime: 1000 * 60 * 60,
  });

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <span className="loading loading-spinner loading-lg text-primary"></span>
      </div>
    );
  }

  if (!categories?.length) {
    return (
      <div className="text-center py-12 text-base-content/50">
        <Squares2X2Icon className="w-12 h-12 mx-auto mb-3 opacity-30" />
      </div>
    );
  }

  return (
    <nav className="pb-6">
      {/* هدر منو */}
      <div className="px-4 py-4 mb-2 border-b border-base-200">
        <h2 className="text-lg font-bold text-base-content flex items-center gap-2">
          <Squares2X2Icon className="w-5 h-5 text-primary" />
          پۆلێنکردنی بەرهەمەکان
        </h2>
      </div>

      {/* لیست دسته‌ها */}
      <ul className="space-y-1 px-2">
        {categories.map((category) => {
          const isExpanded = expandedId === category.id;
          const hasChildren = category.children?.length > 0;

          return (
            <li key={category.id}>
              {/* دسته اصلی */}
              <div
                className={`
                  flex items-center justify-between w-full px-4 py-3.5 rounded-xl
                  transition-all duration-200 cursor-pointer select-none
                  ${
                    isExpanded
                      ? "bg-primary/10 text-primary"
                      : "hover:bg-base-200 text-base-content"
                  }
                `}
                onClick={() => (hasChildren ? toggleExpand(category.id) : null)}
              >
                {hasChildren ? (
                  <>
                    <span className="font-semibold text-[15px]">
                      {category.name}
                    </span>
                    <ChevronDownIcon
                      className={`
                        w-5 h-5 transition-transform duration-300
                        ${isExpanded ? "rotate-180" : ""}
                      `}
                    />
                  </>
                ) : (
                  // دسته بدون زیردسته — مستقیم به shop با فیلتر
                  <Link
                    to={`/shop?category=${category.slug}`}
                    onClick={onClose}
                    className="flex items-center justify-between w-full"
                  >
                    <span className="font-semibold text-[15px]">
                      {category.name}
                    </span>
                    <ChevronLeftIcon className="w-4 h-4 opacity-40" />
                  </Link>
                )}
              </div>

              {/* زیردسته‌ها */}
              {hasChildren && (
                <div
                  className={`
                    overflow-hidden transition-all duration-300 ease-out
                    ${
                      isExpanded
                        ? "max-h-[500px] opacity-100"
                        : "max-h-0 opacity-0"
                    }
                  `}
                >
                  <ul className="py-2 pr-4 space-y-0.5">
                    {/* لینک همه محصولات دسته اصلی */}
                    <li>
                      <Link
                        to={`/shop?category=${category.slug}`}
                        onClick={onClose}
                        className="
                          flex items-center gap-3 px-4 py-2.5 rounded-lg
                          text-primary font-medium text-sm
                          bg-primary/5 hover:bg-primary/10
                          transition-colors duration-200
                        "
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
                        بینینی هەموو {category.name}
                      </Link>
                    </li>

                    {/* زیردسته‌ها — همان الگوی MegaMenu */}
                    {category.children.map((subCategory) => (
                      <li key={subCategory.id}>
                        <Link
                          to={`/shop?category=${subCategory.slug}`}
                          onClick={onClose}
                          className="
                            flex items-center gap-3 px-4 py-2.5 rounded-lg
                            text-base-content/70 text-sm
                            hover:bg-base-200 hover:text-base-content
                            transition-colors duration-200
                          "
                        >
                          <span className="w-1 h-1 rounded-full bg-base-content/30"></span>
                          {subCategory.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </nav>
  );
};

export default MobileMenu;