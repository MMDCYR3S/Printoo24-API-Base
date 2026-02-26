import React from 'react';

const CategoryFilter = ({ categories, activeCategory, onCategoryChange }) => {
  return (
    <div className="w-full overflow-x-auto custom-scrollbar pb-2 mb-6">
      <div className="flex items-center gap-3 min-w-max px-2">
        {/* دکمه "همه مقالات" */}
        <button
          onClick={() => onCategoryChange(null)}
          className={`px-5 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
            activeCategory === null
              ? 'bg-primary text-white shadow-md shadow-primary/30'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          All Articles
        </button>

        {/* لیست دسته‌بندی‌ها */}
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => onCategoryChange(category.id)}
            className={`px-5 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
              activeCategory === category.id
                ? 'bg-primary text-white shadow-md shadow-primary/30'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {category.name}
          </button>
        ))}
      </div>
    </div>
  );
};

export default CategoryFilter;