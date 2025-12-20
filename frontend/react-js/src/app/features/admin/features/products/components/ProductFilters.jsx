// src/app/features/admin/products/components/ProductFilters.jsx
import { Search, Filter, X } from 'lucide-react';

const ProductFilters = ({ 
  searchTerm, onSearchChange, 
  status, onStatusChange, 
  category, onCategoryChange, categories 
}) => {
  return (
    <div className="bg-white p-4 rounded-2xl border border-base-200 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between sticky top-0 z-20 backdrop-blur-xl bg-white/90">
      
      {/* Search */}
      <div className="relative w-full md:w-96 group">
        <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-base-content/40 group-focus-within:text-primary transition-colors" size={20} />
        <input 
          type="text" 
          placeholder="جستجو نام، کد یا اسلاگ..." 
          className="input input-bordered w-full pr-10 focus:border-primary transition-all bg-gray-50 focus:bg-white"
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
        />
        {searchTerm && (
          <button onClick={() => onSearchChange('')} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
            <X size={16} />
          </button>
        )}
      </div>

      {/* Selects */}
      <div className="flex w-full md:w-auto gap-3 overflow-x-auto pb-2 md:pb-0 no-scrollbar">
        
        {/* Category Filter */}
        <select 
          className="select select-bordered w-full md:w-48 text-sm"
          value={category}
          onChange={(e) => onCategoryChange(e.target.value)}
        >
          <option value="all">همه دسته‌بندی‌ها</option>
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>{cat.name}</option>
          ))}
        </select>

        {/* Status Filter */}
        <select 
          className="select select-bordered w-full md:w-40 text-sm"
          value={status}
          onChange={(e) => onStatusChange(e.target.value)}
        >
          <option value="all">همه وضعیت‌ها</option>
          <option value="active">🟢 فعال</option>
          <option value="inactive">🔴 غیرفعال</option>
        </select>
      </div>
    </div>
  );
};

export default ProductFilters;