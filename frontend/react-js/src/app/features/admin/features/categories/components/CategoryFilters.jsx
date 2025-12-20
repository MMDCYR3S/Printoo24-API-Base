import React from 'react';
import { Search, Filter, RefreshCw, SlidersHorizontal } from 'lucide-react';

const CategoryFilters = ({
  searchQuery,
  setSearchQuery,
  statusFilter,
  setStatusFilter,
  parentFilter,
  setParentFilter,
  onRefresh
}) => {
  return (
    <div className="bg-white p-4 rounded-2xl border border-base-200 shadow-sm flex flex-col xl:flex-row gap-4 justify-between items-center animate-fade-in-down">
      
      {/* Search Box */}
      <div className="relative w-full xl:w-96 group">
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400 group-focus-within:text-primary transition-colors" />
        </div>
        <input
          type="text"
          className="input input-bordered w-full pr-10 bg-gray-50 focus:bg-white focus:border-primary focus:ring-4 focus:ring-primary/10 transition-all duration-300"
          placeholder="جستجو در نام، نامک یا توضیحات..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Filters Group */}
      <div className="flex flex-col sm:flex-row w-full xl:w-auto gap-3 items-center">
        
        {/* Status Filter */}
        <div className="w-full sm:w-auto relative">
            <select 
                className="select select-bordered w-full pl-10 bg-white"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
            >
                <option value="all">همه وضعیت‌ها</option>
                <option value="active">فقط فعال‌ها</option>
                <option value="inactive">فقط غیرفعال‌ها</option>
            </select>
            <Filter className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"/>
        </div>

        {/* Parent/Child Filter */}
        <div className="w-full sm:w-auto relative">
            <select 
                className="select select-bordered w-full pl-10 bg-white"
                value={parentFilter}
                onChange={(e) => setParentFilter(e.target.value)}
            >
                <option value="all">همه دسته‌ها</option>
                <option value="root">دسته‌های اصلی (والد)</option>
                <option value="sub">زیردسته‌ها</option>
            </select>
            <SlidersHorizontal className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"/>
        </div>

        <div className="w-px h-8 bg-gray-200 hidden sm:block mx-1"></div>

        {/* Refresh Button */}
        <button 
            onClick={onRefresh}
            className="btn btn-square btn-ghost text-gray-500 hover:text-primary hover:bg-primary/10 transition-colors"
            title="بروزرسانی لیست"
        >
            <RefreshCw size={20} />
        </button>
      </div>
    </div>
  );
};

export default CategoryFilters;