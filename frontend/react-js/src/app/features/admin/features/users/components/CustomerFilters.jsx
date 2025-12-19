// src/app/features/admin/customers/components/CustomerFilters.jsx
import { Search, Download, RefreshCw } from 'lucide-react';

const CustomerFilters = ({ 
  searchTerm, 
  onSearchChange, 
  statusFilter, 
  onStatusChange, 
  roleFilter, 
  onRoleChange,
  onRefresh 
}) => {
  return (
    <div className="bg-base-100 p-4 rounded-2xl border border-base-200 shadow-sm flex flex-col lg:flex-row gap-4 justify-between items-center transition-all hover:shadow-md">
      
      {/* Search Input */}
      <div className="relative w-full lg:w-96 group">
        <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-base-content/40 group-focus-within:text-primary transition-colors" size={20} />
        <input 
          type="text" 
          placeholder="جستجو (نام، موبایل، ایمیل)..." 
          className="input input-bordered w-full pr-10 bg-base-200/50 focus:bg-base-100 focus:border-primary transition-all"
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      {/* Filters & Actions */}
      <div className="flex w-full lg:w-auto gap-3 overflow-x-auto pb-2 lg:pb-0 no-scrollbar">
        
        {/* Status Select */}
        <select 
          className="select select-bordered focus:border-primary w-full sm:w-auto"
          value={statusFilter}
          onChange={(e) => onStatusChange(e.target.value)}
        >
          <option value="all">همه وضعیت‌ها</option>
          <option value="active">فقط فعال‌ها</option>
          <option value="inactive">فقط مسدودها</option>
        </select>

        {/* Role Select */}
        <select 
          className="select select-bordered focus:border-primary w-full sm:w-auto"
          value={roleFilter}
          onChange={(e) => onRoleChange(e.target.value)}
        >
          <option value="all">همه نقش‌ها</option>
          <option value="admin">مدیران و کارمندان</option>
          <option value="user">مشتریان عادی</option>
        </select>
        
        <div className="w-px h-10 bg-base-200 hidden lg:block mx-1"></div>

        {/* Refresh Button */}
        <button 
            onClick={onRefresh} 
            className="btn btn-square btn-ghost hover:bg-base-200 text-base-content/60"
            title="بروزرسانی لیست"
        >
            <RefreshCw size={20} />
        </button>

        {/* Export Button */}
        <button className="btn btn-square btn-ghost hover:bg-base-200 text-base-content/60" title="خروجی اکسل">
          <Download size={20} />
        </button>
      </div>
    </div>
  );
};

export default CustomerFilters;