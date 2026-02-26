import React from 'react';
import { Search, ListFilter, ArrowDownWideNarrow } from 'lucide-react';

const BlogSidebar = ({ categories, filters, onFilterChange }) => {
  return (
    <aside className="w-full lg:w-80 flex-shrink-0 space-y-6 lg:sticky lg:top-24 h-fit">
      


      {/* ── بخش مرتب‌سازی ── */}
        <div className="bg-radial from-white from-50% to-slate-100 p-5 rounded-2xl border border-slate-100 ">
        <div className="flex items-center gap-2 mb-4">
          <ArrowDownWideNarrow size={18} className="text-primary" />
          <h3 className="font-bold text-slate-800">Sort By</h3>
        </div>
        <select
          value={filters.ordering}
          onChange={(e) => onFilterChange('ordering', e.target.value)}
          className="w-full bg-radial inset-shadow inset-shadow-sm border border-slate-200 text-slate-700 text-sm rounded-xl px-4 py-3 focus:outline-none focus:border-primary transition-all appearance-none cursor-pointer"
        >
          <option value="-published_at">Newest First</option>
          <option value="published_at">Oldest First</option>
          <option value="-views_count">Most Popular</option>
          <option value="-read_time">Longest Read</option>
        </select>
      </div>

      {/* ── بخش دسته‌بندی‌ها ── */}
      <div className=" bg-radial from-50% from-white to-slate-100 p-5 rounded-2xl border border-slate-100 ">
        <div className="flex items-center gap-2 mb-4">
          <ListFilter size={18} className="text-primary" />
          <h3 className="font-bold text-slate-800">Categories</h3>
        </div>
        <div className="flex flex-col gap-2">
          <button
            onClick={() => onFilterChange('category', null)}
            className={`text-left px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
              !filters.categoryId
                ? 'bg-primary/10 text-primary'
                : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            All Categories
          </button>
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => onFilterChange('category', category.id.toString())}
              className={`text-left px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                filters.categoryId === category.id.toString()
                  ? 'bg-primary/10 text-primary'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              {category.name}
            </button>
          ))}
        </div>
      </div>

    </aside>
  );
};

export default BlogSidebar;