// src/app/features/admin/articles/components/ArticleFilters.jsx
import React from 'react';
import { Search, Filter, RefreshCw } from 'lucide-react';

const ArticleFilters = ({ 
  searchQuery, 
  setSearchQuery, 
  statusFilter, 
  setStatusFilter, 
  onRefresh 
}) => {
  return (
    <div className="bg-white/80 backdrop-blur-xl p-4 rounded-2xl border border-slate-100 shadow-lg shadow-slate-200/20 flex flex-col md:flex-row gap-4 items-center justify-between mb-6 z-20 relative">
      
      {/* بخش جستجو */}
      <div className="relative w-full md:w-96 group">
        <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-primary transition-colors">
          <Search size={18} />
        </div>
        <input
          type="text"
          placeholder="جستجو در عنوان مقالات..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input w-full bg-slate-50 border-slate-200 focus:border-primary focus:ring-2 focus:ring-primary/20 rounded-xl pr-12 text-sm transition-all placeholder:text-slate-400"
        />
      </div>

      {/* بخش فیلترها و رفرش */}
      <div className="flex items-center gap-3 w-full md:w-auto">
        <div className="relative flex-1 md:flex-none">
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-slate-400">
            <Filter size={16} />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="select w-full md:w-48 bg-slate-50 border-slate-200 focus:border-primary focus:ring-2 focus:ring-primary/20 rounded-xl pr-10 text-sm transition-all"
          >
            <option value="all">همه وضعیت‌ها</option>
            <option value="published">منتشر شده</option>
            <option value="draft">پیش‌نویس</option>
            <option value="archived">بایگانی شده</option>
          </select>
        </div>

        <button 
          onClick={onRefresh}
          className="btn btn-square bg-slate-50 border-slate-200 text-slate-500 hover:bg-white hover:border-primary hover:text-primary transition-all rounded-xl tooltip tooltip-top"
          data-tip="بروزرسانی لیست"
        >
          <RefreshCw size={18} />
        </button>
      </div>
    </div>
  );
};

export default ArticleFilters;