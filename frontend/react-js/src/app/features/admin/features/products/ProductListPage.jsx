// src/app/features/admin/products/ProductListPage.jsx
import { useState } from 'react';
import { useAdminProducts } from './hooks/useAdminProducts';
import { Package, Plus, ArrowUp, ArrowDown, Image as ImageIcon } from 'lucide-react';
import ProductFilters from './components/ProductFilters';
import BulkActionsBar from './components/BulkActionsBar';
import clsx from 'clsx';

const ProductListPage = () => {
  const {
    products, totalItems, totalPages, currentPage, setCurrentPage,
    searchQuery, setSearchQuery,
    categoryFilter, setCategoryFilter,
    statusFilter, setStatusFilter, categories,
    sortConfig, handleSort,
    isLoading,
    bulkDeleteMutation, bulkStatusMutation
  } = useAdminProducts();

  // State برای آیتم‌های انتخاب شده
  const [selectedIds, setSelectedIds] = useState([]);

  // --- Selection Handlers ---
  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedIds(products.map(p => p.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (id) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleBulkDelete = () => {
    if (confirm(`آیا مطمئن هستید که می‌خواهید ${selectedIds.length} محصول را حذف کنید؟`)) {
      bulkDeleteMutation.mutate(selectedIds);
      setSelectedIds([]);
    }
  };

  const handleBulkStatus = (isActive) => {
    bulkStatusMutation.mutate({ product_ids: selectedIds, is_active: isActive });
    setSelectedIds([]);
  };

  // --- Formatters ---
  const formatPrice = (price) => new Intl.NumberFormat('fa-IR').format(Number(price));

  // --- Table Header Component ---
  const Th = ({ label, sortKey, className }) => (
    <th 
      className={clsx("cursor-pointer hover:bg-base-200 transition-colors select-none", className)}
      onClick={() => sortKey && handleSort(sortKey)}
    >
      <div className="flex items-center gap-1">
        {label}
        {sortKey && sortConfig.key === sortKey && (
          sortConfig.direction === 'asc' ? <ArrowUp size={14} className="text-primary"/> : <ArrowDown size={14} className="text-primary"/>
        )}
      </div>
    </th>
  );

  return (
    <div className="p-4 md:p-8 min-h-screen bg-base-100/50 space-y-6 pb-24">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-800 flex items-center gap-2">
            <Package className="text-primary" size={32} />
            مدیریت محصولات
          </h1>
          <p className="text-slate-500 mt-1 text-sm font-medium">
            لیست کامل {totalItems} محصول | مدیریت موجودی و قیمت‌ها
          </p>
        </div>
        <button className="btn btn-primary px-6 shadow-lg shadow-primary/30 text-white gap-2 rounded-xl">
          <Plus size={20} /> محصول جدید
        </button>
      </div>

      {/* Filters */}
      <ProductFilters 
        searchTerm={searchQuery} onSearchChange={setSearchQuery}
        category={categoryFilter} onCategoryChange={setCategoryFilter} categories={categories}
        status={statusFilter} onStatusChange={setStatusFilter}
      />

      {/* Table Content */}
      <div className="bg-white rounded-3xl border border-base-200 shadow-xl shadow-base-200/50 overflow-hidden">
        {isLoading ? (
          <div className="p-20 flex flex-col items-center justify-center gap-4 text-primary">
            <span className="loading loading-spinner loading-lg"></span>
            <span className="text-slate-400 text-sm">در حال بارگذاری محصولات...</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table w-full">
              {/* Table Head */}
              <thead className="bg-slate-50/80 text-slate-500 text-xs uppercase font-bold tracking-wider">
                <tr>
                  <th className="w-12">
                    <label>
                      <input 
                        type="checkbox" 
                        className="checkbox checkbox-sm rounded-md checkbox-primary"
                        onChange={handleSelectAll}
                        checked={products.length > 0 && selectedIds.length === products.length}
                      />
                    </label>
                  </th>
                  <Th label="تصویر" className="w-20"/>
                  <Th label="نام محصول" sortKey="name" />
                  <Th label="کد (SKU)" sortKey="code" />
                  <Th label="دسته‌بندی" sortKey="category" />
                  <Th label="قیمت پایه" sortKey="price" />
                  <Th label="وضعیت" sortKey="is_active" className="text-center" />
                  <th className="text-center">عملیات</th>
                </tr>
              </thead>
              
              {/* Table Body */}
              <tbody className="divide-y divide-slate-100">
                {products.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="text-center py-20 text-slate-400">
                      محصولی یافت نشد :/
                    </td>
                  </tr>
                ) : (
                  products.map((product) => {
                    const isSelected = selectedIds.includes(product.id);
                    return (
                      <tr 
                        key={product.id} 
                        className={clsx(
                          "hover:bg-slate-50 transition-colors group",
                          isSelected && "bg-primary/5 hover:bg-primary/10"
                        )}
                      >
                        {/* Checkbox */}
                        <th>
                          <label>
                            <input 
                              type="checkbox" 
                              className="checkbox checkbox-sm rounded-md checkbox-primary"
                              checked={isSelected}
                              onChange={() => handleSelectOne(product.id)}
                            />
                          </label>
                        </th>

                        {/* Image */}
                        <td>
                          <div className="avatar">
                            <div className="w-12 h-12 rounded-xl ring-1 ring-slate-100 bg-slate-50 flex items-center justify-center">
                              {product.images && product.images.length > 0 ? (
                                <img src={product.images[0].image} alt={product.name} className="object-cover" />
                              ) : (
                                <ImageIcon size={20} className="text-slate-300" />
                              )}
                            </div>
                          </div>
                        </td>

                        {/* Name */}
                        <td>
                          <div className="flex flex-col gap-1">
                            <span className="font-bold text-slate-800 text-sm line-clamp-1 group-hover:text-primary transition-colors">
                              {product.name}
                            </span>
                            <span className="text-[10px] text-slate-400 font-mono hidden md:inline-block">
                              {product.slug}
                            </span>
                          </div>
                        </td>

                        {/* SKU */}
                        <td>
                           <span className="badge badge-ghost badge-sm font-mono text-[10px] text-slate-500">
                             {product.code.split('-')[0]}...
                           </span>
                        </td>

                        {/* Category */}
                        <td>
                           {/* اینجا چون فقط آیدی داریم، اگر لیست کتگوری‌ها لود شده باشه اسمش رو نشون میدیم */}
                           <span className="text-xs font-medium text-slate-600 bg-slate-100 px-2 py-1 rounded-lg">
                             {categories.find(c => c.id === product.category)?.name || `ID: ${product.category}`}
                           </span>
                        </td>

                        {/* Price */}
                        <td>
                           {product.has_price ? (
                             <div className="font-bold text-slate-700 text-sm dir-ltr text-right">
                               {formatPrice(product.price)} <span className="text-[10px] text-slate-400">IQD</span>
                             </div>
                           ) : (
                             <span className="badge badge-warning badge-outline text-xs">تماس بگیرید</span>
                           )}
                        </td>

                        {/* Status */}
                        <td className="text-center">
                           <div className={clsx(
                             "badge badge-sm gap-1 border-none px-3 py-2",
                             product.is_active ? "bg-emerald-100 text-emerald-600" : "bg-red-100 text-red-600"
                           )}>
                             <div className={clsx("w-1.5 h-1.5 rounded-full", product.is_active ? "bg-emerald-500" : "bg-red-500")}></div>
                             {product.is_active ? 'فعال' : 'غیرفعال'}
                           </div>
                        </td>

                        {/* Actions */}
                        <td>
                           <div className="flex justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                              <button className="btn btn-sm btn-ghost btn-square text-blue-500 hover:bg-blue-50">
                                <Plus size={16}/> {/* ویرایش فرضی */}
                              </button>
                           </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}
        
        {/* Pagination Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between text-sm">
           <span className="text-slate-400">
             نمایش صفحه <span className="font-bold text-slate-700">{currentPage}</span> از {totalPages}
           </span>
           <div className="join bg-white shadow-sm border border-slate-200">
              <button 
                className="join-item btn btn-sm btn-ghost disabled:bg-transparent" 
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(p => p - 1)}
              >
                «
              </button>
              {Array.from({ length: totalPages }, (_, i) => (
                <button 
                  key={i} 
                  className={clsx(
                    "join-item btn btn-sm",
                    currentPage === i + 1 ? "btn-primary text-white" : "btn-ghost"
                  )}
                  onClick={() => setCurrentPage(i + 1)}
                >
                  {i + 1}
                </button>
              ))}
              <button 
                className="join-item btn btn-sm btn-ghost disabled:bg-transparent" 
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage(p => p + 1)}
              >
                »
              </button>
           </div>
        </div>
      </div>

      {/* Bulk Actions Bar (Floating) */}
      <BulkActionsBar 
        selectedCount={selectedIds.length}
        onClear={() => setSelectedIds([])}
        onDelete={handleBulkDelete}
        onStatusChange={handleBulkStatus}
      />

    </div>
  );
};

export default ProductListPage;