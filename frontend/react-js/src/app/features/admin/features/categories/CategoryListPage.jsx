// src/app/features/admin/categories/CategoryListPage.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom'; // 👈 اضافه شد
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, Edit, Trash2, Eye, CheckCircle2, XCircle, 
  ArrowUp, ArrowDown, ChevronLeft, ChevronRight, Layers, CornerDownLeft, MoreHorizontal 
} from 'lucide-react';
import { useAdminCategories } from '../../hooks/useAdminCategories'; // مسیر هوک را چک کنید
import CategoryFilters from './components/CategoryFilters'; // مسیر کامپوننت فیلتر را چک کنید
import clsx from 'clsx';

const CategoryListPage = () => {
  const navigate = useNavigate();
  
  const {
    categories,
    totalItems,
    totalPages,
    currentPage,
    setCurrentPage,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    parentFilter,
    setParentFilter,
    sortConfig,
    handleSort,
    isLoading,
    toggleStatusMutation,
    deleteMutation,
    bulkDeleteMutation,
  } = useAdminCategories();

  // State های لوکال
  const [selectedIds, setSelectedIds] = useState([]);

  // --- Handlers ---

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedIds(categories.map(c => c.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (id) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(itemId => itemId !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleDelete = (id) => {
    if (window.confirm('آیا مطمئن هستید؟ حذف دسته ممکن است روی محصولات تاثیر بگذارد.')) {
      deleteMutation.mutate(id);
    }
  };

  const handleBulkDelete = () => {
    if (window.confirm(`آیا مطمئن هستید ${selectedIds.length} مورد حذف شود؟`)) {
      bulkDeleteMutation.mutate(selectedIds, {
        onSuccess: () => setSelectedIds([])
      });
    }
  };

  const handleBulkStatus = (status) => {
    toggleStatusMutation.mutate({ ids: selectedIds, active: status }, {
        onSuccess: () => setSelectedIds([])
    });
  };

  // --- Helper Components ---
  
  const ThSortable = ({ label, sortKey, className }) => (
    <th 
      onClick={() => handleSort(sortKey)}
      className={clsx("cursor-pointer hover:bg-base-200 transition-colors select-none py-4", className)}
    >
      <div className="flex items-center gap-2 text-slate-600">
        {label}
        {sortConfig.key === sortKey && (
          sortConfig.direction === 'asc' 
            ? <ArrowUp size={14} className="text-primary"/> 
            : <ArrowDown size={14} className="text-primary"/>
        )}
      </div>
    </th>
  );

  return (
    <div className="p-4 md:p-8 max-w-[1920px] mx-auto min-h-screen space-y-6 pb-32 animate-fade-in">
      
      {/* --- HEADER --- */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-800 flex items-center gap-3">
            <span className="p-3 bg-gradient-to-br from-primary/10 to-primary/5 text-primary rounded-2xl shadow-sm border border-primary/10">
                <Layers size={28} />
            </span>
            مدیریت دسته‌بندی‌ها
          </h1>
          <p className="text-slate-500 mt-2 text-sm font-medium pr-1">
            لیست کامل و مدیریت ساختار درختی محصولات
            <span className="inline-flex items-center justify-center px-2 py-0.5 mr-2 rounded-full bg-slate-100 text-slate-600 text-xs font-bold border border-slate-200">
              {totalItems} مورد
            </span>
          </p>
        </div>
        
        <Link 
            to="create" // 👈 لینک به صفحه ساخت
            className="btn btn-primary px-6 shadow-lg shadow-primary/30 hover:scale-105 transition-all duration-300 h-12 text-base"
        >
          <Plus size={20} />
          افزودن دسته جدید
        </Link>
      </div>

      {/* --- FILTERS --- */}
      <div className="sticky top-2 z-20">
        <CategoryFilters 
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            parentFilter={parentFilter}
            setParentFilter={setParentFilter}
            onRefresh={() => window.location.reload()}
        />
      </div>

      {/* --- TABLE --- */}
      <div className="bg-white rounded-[2rem] border border-slate-100 shadow-xl shadow-slate-200/40 overflow-hidden relative min-h-[500px]">
        {isLoading && (
            <div className="absolute inset-0 bg-white/60 z-10 flex items-center justify-center backdrop-blur-[2px]">
                <div className="flex flex-col items-center gap-3">
                    <span className="loading loading-spinner loading-lg text-primary"></span>
                    <span className="text-sm font-bold text-slate-400">در حال دریافت لیست...</span>
                </div>
            </div>
        )}

        <div className="overflow-x-auto">
          <table className="table w-full">
            <thead className="bg-slate-50/80 text-xs uppercase font-bold tracking-wider border-b border-slate-100 backdrop-blur-md">
              <tr>
                <th className="w-16 text-center">
                  <label>
                    <input 
                        type="checkbox" 
                        className="checkbox checkbox-sm checkbox-primary rounded-md transition-all"
                        checked={categories.length > 0 && selectedIds.length === categories.length}
                        onChange={handleSelectAll}
                    />
                  </label>
                </th>
                <th className="w-24">تصویر</th>
                <ThSortable label="نام دسته‌بندی" sortKey="name" />
                <ThSortable label="نامک (Slug)" sortKey="slug" />
                <th>دسته مادر</th>
                <ThSortable label="وضعیت" sortKey="is_active" className="text-center" />
                <th className="text-left pl-6 w-40">عملیات</th>
              </tr>
            </thead>
            
            <tbody className="divide-y divide-slate-50">
              {categories.length === 0 && !isLoading ? (
                  <tr>
                      <td colSpan="7" className="text-center py-24 text-slate-400">
                          <div className="flex flex-col items-center gap-4 opacity-60">
                              <Layers size={64} strokeWidth={1}/>
                              <span className="text-lg">هیچ دسته‌بندی یافت نشد!</span>
                          </div>
                      </td>
                  </tr>
              ) : (
                  categories.map((cat) => (
                    <tr 
                        key={cat.id} 
                        className={clsx(
                            "group hover:bg-blue-50/30 transition-colors duration-200",
                            selectedIds.includes(cat.id) && "bg-blue-50/60"
                        )}
                    >
                      {/* Checkbox */}
                      <th className="text-center">
                        <label>
                          <input 
                            type="checkbox" 
                            className="checkbox checkbox-sm checkbox-primary rounded-md"
                            checked={selectedIds.includes(cat.id)}
                            onChange={() => handleSelectOne(cat.id)}
                          />
                        </label>
                      </th>

                      {/* Image */}
                      <td>
                        <Link to={`${cat.id}`}>
                            <div className="avatar">
                            <div className="w-14 h-14 rounded-2xl ring-1 ring-slate-100 shadow-sm bg-white p-0.5 transition-transform group-hover:scale-110 group-hover:shadow-md">
                                {cat.banner_box ? (
                                    <img src={cat.banner_box} alt={cat.name} className="object-cover rounded-xl" />
                                ) : (
                                    <div className="w-full h-full bg-slate-50 flex items-center justify-center text-slate-300 rounded-xl">
                                        <Layers size={24}/>
                                    </div>
                                )}
                            </div>
                            </div>
                        </Link>
                      </td>

                      {/* Name */}
                      <td>
                        <Link to={`${cat.id}`} className="block group/link">
                            <div className="font-bold text-slate-700 text-base group-hover/link:text-primary transition-colors">
                                {cat.name}
                            </div>
                            {cat.children_count > 0 ? (
                                <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1 font-medium bg-slate-100 w-fit px-2 py-0.5 rounded-md">
                                    <CornerDownLeft size={10} />
                                    {cat.children_count} زیردسته
                                </div>
                            ) : (
                                <div className="text-[11px] text-slate-300 mt-1">بدون زیردسته</div>
                            )}
                        </Link>
                      </td>

                      {/* Slug */}
                      <td>
                        <div className="badge badge-ghost font-mono text-xs opacity-60 dir-ltr bg-slate-100 text-slate-500 border-0">
                            /{cat.slug}
                        </div>
                      </td>

                      {/* Parent */}
                      <td>
                        {cat.parent_name ? (
                            <Link to={`${cat.parent}`} className="badge badge-outline text-xs text-slate-500 border-slate-300 bg-white hover:bg-slate-50 hover:border-slate-400 transition-all gap-1 pl-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
                                {cat.parent_name}
                            </Link>
                        ) : (
                            <span className="text-[10px] text-primary font-bold bg-primary/5 px-2 py-1 rounded-lg border border-primary/10">
                                ریشه (Root)
                            </span>
                        )}
                      </td>

                      {/* Status Toggle */}
                      <td className="text-center">
                        <button 
                            onClick={() => toggleStatusMutation.mutate({ ids: [cat.id], active: !cat.is_active })}
                            className={clsx(
                                "badge gap-1.5 py-3 px-3 border-0 transition-all cursor-pointer shadow-sm hover:shadow-md hover:scale-105 active:scale-95 font-medium",
                                cat.is_active 
                                    ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-200" 
                                    : "bg-red-100 text-red-700 hover:bg-red-200"
                            )}
                        >
                            {cat.is_active ? <CheckCircle2 size={14} strokeWidth={2.5}/> : <XCircle size={14} strokeWidth={2.5}/>}
                            {cat.is_active ? 'فعال' : 'غیرفعال'}
                        </button>
                      </td>

                      {/* Actions */}
                      <td>
                        <div className="flex justify-end items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity">
                            <Link 
                                to={`${cat.id}`}
                                className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-primary hover:bg-primary/10 tooltip tooltip-top"
                                data-tip="مشاهده جزئیات"
                            >
                                <Eye size={18} />
                            </Link>
                            
                            <Link 
                                to={`edit/${cat.id}`} // 👈 لینک به صفحه ادیت
                                className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-blue-600 hover:bg-blue-50 tooltip tooltip-top"
                                data-tip="ویرایش"
                            >
                                <Edit size={18} />
                            </Link>

                            <div className="w-px h-4 bg-slate-200 mx-1"></div>

                            <button 
                                onClick={() => handleDelete(cat.id)}
                                className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-red-500 hover:bg-red-50 tooltip tooltip-top"
                                data-tip="حذف"
                            >
                                <Trash2 size={18} />
                            </button>
                        </div>
                      </td>
                    </tr>
                  ))
              )}
            </tbody>
          </table>
        </div>

        {/* --- PAGINATION --- */}
        <div className="p-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-50/50">
            <div className="text-xs text-slate-500 font-medium">
                نمایش {(currentPage - 1) * 10 + 1} تا {Math.min(currentPage * 10, totalItems)} از {totalItems} رکورد
            </div>
            
            <div className="join bg-white shadow-sm border border-slate-200 rounded-xl overflow-hidden">
                <button 
                    className="join-item btn btn-sm btn-ghost disabled:bg-transparent px-4 hover:bg-slate-50"
                    disabled={currentPage === 1}
                    onClick={() => setCurrentPage(p => p - 1)}
                >
                    <ChevronRight size={16}/>
                    <span className="hidden sm:inline text-xs">قبلی</span>
                </button>
                <button className="join-item btn btn-sm btn-ghost pointer-events-none font-mono text-slate-700 border-x border-slate-100 px-4">
                    صفحه {currentPage}
                </button>
                <button 
                    className="join-item btn btn-sm btn-ghost disabled:bg-transparent px-4 hover:bg-slate-50"
                    disabled={currentPage === totalPages}
                    onClick={() => setCurrentPage(p => p + 1)}
                >
                    <span className="hidden sm:inline text-xs">بعدی</span>
                    <ChevronLeft size={16}/>
                </button>
            </div>
        </div>
      </div>

      {/* --- FLOATING BULK ACTIONS --- */}
      <AnimatePresence>
        {selectedIds.length > 0 && (
            <motion.div 
                initial={{ y: 100, opacity: 0, scale: 0.9 }}
                animate={{ y: 0, opacity: 1, scale: 1 }}
                exit={{ y: 100, opacity: 0, scale: 0.9 }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="fixed bottom-8 left-1/2 -translate-x-1/2 z-[50] flex items-center gap-4 bg-slate-900/90 text-white pl-3 pr-6 py-3 rounded-2xl shadow-2xl shadow-slate-900/30 border border-slate-700/50 backdrop-blur-md"
            >
                <div className="flex items-center gap-3 border-l border-white/10 pl-4">
                    <div className="badge badge-primary font-bold shadow-lg shadow-primary/40">{selectedIds.length}</div>
                    <span className="text-sm font-medium">مورد انتخاب شد</span>
                </div>
                
                <div className="flex items-center gap-1">
                    <button 
                        onClick={() => handleBulkStatus(true)}
                        className="btn btn-ghost btn-sm text-emerald-400 hover:bg-emerald-500/20 hover:text-emerald-300 gap-2 font-normal"
                    >
                        <CheckCircle2 size={18} />
                        <span className="hidden sm:inline">فعال‌سازی</span>
                    </button>
                    <button 
                        onClick={() => handleBulkStatus(false)}
                        className="btn btn-ghost btn-sm text-amber-400 hover:bg-amber-500/20 hover:text-amber-300 gap-2 font-normal"
                    >
                        <XCircle size={18} />
                        <span className="hidden sm:inline">مسدودسازی</span>
                    </button>
                    <button 
                        onClick={handleBulkDelete}
                        className="btn btn-ghost btn-sm text-red-400 hover:bg-red-500/20 hover:text-red-300 gap-2 font-normal"
                    >
                        <Trash2 size={18} />
                        <span className="hidden sm:inline">حذف</span>
                    </button>
                </div>
                
                <button 
                    onClick={() => setSelectedIds([])}
                    className="btn btn-circle btn-xs btn-ghost text-white/40 hover:text-white hover:bg-white/10 transition-colors mr-2"
                >
                    ×
                </button>
            </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CategoryListPage;