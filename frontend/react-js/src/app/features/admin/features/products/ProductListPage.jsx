// src/app/features/admin/products/ProductListPage.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Package, Search, Filter, Plus, Edit, Eye, // Eye اضافه شد
  ArrowUp, ArrowDown, Image as ImageIcon, 
  CheckCircle2, XCircle, Trash2, RefreshCw, Box, Layers, MoreHorizontal
} from 'lucide-react';
import clsx from 'clsx';
import { useAdminProducts } from './hooks/useAdminProducts';
import BulkActionsBar from './components/BulkActionsBar'; 

const ProductListPage = () => {
  const navigate = useNavigate();
  const {
    products, stats, totalItems, totalPages, currentPage, setCurrentPage,
    searchQuery, setSearchQuery,
    categoryFilterId, setCategoryFilterId,
    statusFilter, setStatusFilter,
    categories,
    sortConfig, handleSort,
    isLoading, refetch,
    bulkDeleteMutation, bulkStatusMutation
  } = useAdminProducts();

  const [selectedIds, setSelectedIds] = useState([]);

  // --- Handlers ---
  const handleSelectAll = (e) => {
    setSelectedIds(e.target.checked ? products.map(p => p.id) : []);
  };

  const handleSelectOne = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const handleDeleteOne = (id) => {
    if (confirm('آیا از حذف این محصول اطمینان دارید؟')) {
        bulkDeleteMutation.mutate([id]);
    }
  };

  const handleBulkDelete = () => {
    if (confirm(`آیا از حذف ${selectedIds.length} محصول اطمینان دارید؟`)) {
      bulkDeleteMutation.mutate(selectedIds, { onSuccess: () => setSelectedIds([]) });
    }
  };

  const handleBulkStatus = (isActive) => {
    bulkStatusMutation.mutate({ product_ids: selectedIds, is_active: isActive }, { onSuccess: () => setSelectedIds([]) });
  };

  const formatPrice = (price) => new Intl.NumberFormat('fa-IR').format(Number(price));

  // --- Components ---
  const SortableTh = ({ label, sortKey, className }) => (
    <th 
      onClick={() => sortKey && handleSort(sortKey)}
      className={clsx("py-4 text-xs font-bold text-slate-500 uppercase cursor-pointer hover:bg-slate-100 transition-colors select-none", className)}
    >
      <div className="flex items-center gap-1">
        {label}
        {sortKey && sortConfig.key === sortKey && (
          <span className="text-primary animate-in fade-in zoom-in">
            {sortConfig.direction === 'asc' ? <ArrowUp size={14}/> : <ArrowDown size={14}/>}
          </span>
        )}
      </div>
    </th>
  );

  const StatCard = ({ title, value, icon: Icon, colorClass }) => (
    <div className="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-4 transition-transform hover:scale-[1.02]">
      <div className={`p-3 rounded-xl ${colorClass}`}>
        <Icon size={24} />
      </div>
      <div>
        <p className="text-slate-500 text-xs font-bold mb-1">{title}</p>
        <h4 className="text-2xl font-black text-slate-800">{value}</h4>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50/50 p-6 md:p-8 pb-32 font-sans space-y-6">
      
      {/* Header & Stats ... (مثل قبل) */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-3xl font-black text-slate-800 flex items-center gap-3">
            <span className="w-3 h-8 rounded-full bg-primary block"></span>
            مدیریت محصولات
          </h1>
          <p className="text-slate-500 mt-2 text-sm font-medium">
            لیست کامل و مدیریت موجودی انبار ({totalItems} مورد یافت شد)
          </p>
        </div>
        
        <div className="flex gap-3">
            <button onClick={() => refetch()} className="btn btn-ghost btn-circle text-slate-400 hover:text-primary tooltip tooltip-bottom" data-tip="بروزرسانی">
                <RefreshCw size={20} className={isLoading ? "animate-spin" : ""} />
            </button>
            <Link to="/admin/products/create" className="btn btn-primary px-6 shadow-xl shadow-primary/20 rounded-2xl h-12 text-base gap-2 hover:scale-105 transition-transform">
                <Plus size={20} /> محصول جدید
            </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
         <StatCard title="کل محصولات" value={stats?.total || 0} icon={Package} colorClass="bg-blue-50 text-blue-600" />
         <StatCard title="محصولات فعال" value={stats?.active || 0} icon={CheckCircle2} colorClass="bg-emerald-50 text-emerald-600" />
         <StatCard title="غیرفعال / ناموجود" value={stats?.inactive || 0} icon={Box} colorClass="bg-red-50 text-red-600" />
      </div>

      {/* Filters Bar ... (مثل قبل) */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col xl:flex-row gap-4 items-center justify-between sticky top-2 z-30 backdrop-blur-xl bg-white/95">
        <div className="relative w-full xl:w-96 group">
          <Search className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-primary transition-colors" size={20} />
          <input 
            type="text" placeholder="جستجو در نام، کد و دسته‌بندی..." 
            className="input input-bordered w-full pr-11 bg-slate-50 focus:bg-white focus:border-primary rounded-xl transition-all h-12"
            value={searchQuery} onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
          />
        </div>
        <div className="flex flex-col sm:flex-row w-full xl:w-auto gap-3">
           <div className="relative w-full sm:w-64">
             <Filter className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={16}/>
             <select 
                className="select select-bordered w-full pr-10 rounded-xl text-sm font-medium h-12"
                value={categoryFilterId} onChange={(e) => { setCategoryFilterId(e.target.value); setCurrentPage(1); }}
             >
                <option value="all">همه دسته‌بندی‌ها</option>
                {categories.map(cat => (<option key={cat.id} value={cat.id}>{cat.name}</option>))}
             </select>
           </div>
           <select 
              className="select select-bordered w-full sm:w-48 rounded-xl text-sm font-medium h-12"
              value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setCurrentPage(1); }}
           >
              <option value="all">همه وضعیت‌ها</option>
              <option value="active">فقط فعال‌ها</option>
              <option value="inactive">فقط غیرفعال‌ها</option>
           </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-[2rem] border border-slate-100 shadow-xl shadow-slate-200/50 overflow-hidden relative min-h-[500px]">
        <AnimatePresence>
            {isLoading && (
                <div className="absolute inset-0 bg-white/80 z-20 flex flex-col items-center justify-center backdrop-blur-sm">
                    <span className="loading loading-spinner loading-lg text-primary mb-4"></span>
                    <p className="text-slate-500 font-bold animate-pulse">در حال بارگذاری اطلاعات...</p>
                </div>
            )}
        </AnimatePresence>

        <div className="overflow-x-auto">
          <table className="table w-full">
            <thead className="bg-slate-50/80 border-b border-slate-100 backdrop-blur-md">
              <tr>
                <th className="w-16 text-center">
                  <label><input type="checkbox" className="checkbox checkbox-sm checkbox-primary rounded-md" checked={products.length > 0 && selectedIds.length === products.length} onChange={handleSelectAll}/></label>
                </th>
                <th className="px-4 py-4 w-24">تصویر</th>
                <SortableTh label="نام محصول" sortKey="name" />
                <SortableTh label="دسته‌بندی" sortKey="category" />
                <SortableTh label="کد محصول" sortKey="code" />
                <SortableTh label="قیمت پایه" sortKey="price" />
                <SortableTh label="وضعیت" sortKey="is_active" className="text-center" />
                <th className="px-4 py-4 text-center text-xs font-bold text-slate-500 uppercase">عملیات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {products.length === 0 && !isLoading ? (
                  <tr><td colSpan="8" className="text-center py-32 text-slate-400">هیچ محصولی یافت نشد!</td></tr>
              ) : (
                  products.map((product) => (
                    <motion.tr 
                        key={product.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                        className={clsx("group hover:bg-slate-50 transition-colors duration-200", selectedIds.includes(product.id) && "bg-blue-50/50")}
                    >
                      <td className="text-center">
                        <label><input type="checkbox" className="checkbox checkbox-sm checkbox-primary rounded-md" checked={selectedIds.includes(product.id)} onChange={() => handleSelectOne(product.id)}/></label>
                      </td>
                      <td>
                        <div className="avatar">
                            <div className="w-14 h-14 rounded-2xl ring-1 ring-slate-100 bg-white p-1 shadow-sm group-hover:scale-105 transition-transform">
                                {product.images && product.images.length > 0 ? (
                                    <img src={product.images[0].image} alt={product.name} className="object-cover rounded-xl" />
                                ) : (
                                    <div className="w-full h-full bg-slate-50 flex items-center justify-center rounded-xl text-slate-300"><ImageIcon size={20}/></div>
                                )}
                            </div>
                        </div>
                      </td>
                      <td>
                        <div className="flex flex-col">
                            {/* لینک نام به صفحه جزئیات */}
                            <Link to={`${product.id}`} className="font-bold text-slate-700 text-sm group-hover:text-primary transition-colors">
                                {product.name}
                            </Link>
                            <span className="text-[10px] text-slate-400 font-mono mt-1 opacity-70 dir-ltr text-right truncate w-fit">/{product.slug}</span>
                        </div>
                      </td>
                      <td>
                        <div className="badge badge-ghost gap-1 pl-2 pr-2.5 py-3 rounded-lg text-slate-600 bg-slate-100 border-0">
                           <Layers size={12} className="opacity-50"/><span className="text-xs font-bold">{product.category || 'بدون دسته'}</span>
                        </div>
                      </td>
                      <td><span className="font-mono text-xs text-slate-500 bg-white px-2 py-1 rounded border border-slate-200">{product.code?.split('-')[0] || '---'}</span></td>
                      <td>
                        {product.has_price ? (
                            <div className="flex items-center gap-1 font-bold text-slate-700 dir-ltr text-right">
                                {formatPrice(product.price)} <span className="text-[10px] text-slate-400 font-normal">IQD</span>
                            </div>
                        ) : <span className="badge badge-xs badge-warning badge-outline">تماس بگیرید</span>}
                      </td>
                      <td className="text-center">
                         {product.is_active ? (
                            <div className="badge badge-success badge-sm gap-1 text-white shadow-lg shadow-success/20 py-3"><CheckCircle2 size={12}/> فعال</div>
                         ) : (
                            <div className="badge badge-error badge-sm gap-1 text-white shadow-lg shadow-error/20 py-3"><XCircle size={12}/> غیرفعال</div>
                         )}
                      </td>
                      <td>
                        <div className="flex justify-center gap-1 items-center opacity-100">
                            {/* دکمه مشاهده */}
                            <Link to={`${product.id}`} className="btn btn-sm btn-ghost btn-square text-slate-500 hover:bg-slate-100 tooltip tooltip-top" data-tip="مشاهده جزئیات">
                                <Eye size={18}/>
                            </Link>
                            {/* دکمه ویرایش */}
                            <Link to={`edit/${product.id}`} className="btn btn-sm btn-ghost btn-square text-blue-600 hover:bg-blue-50 tooltip tooltip-top" data-tip="ویرایش محصول">
                                <Edit size={18}/>
                            </Link>
                            {/* دکمه حذف */}
                            <button onClick={() => handleDeleteOne(product.id)} className="btn btn-sm btn-ghost btn-square text-red-500 hover:bg-red-50 tooltip tooltip-top" data-tip="حذف محصول">
                                <Trash2 size={18}/>
                            </button>
                        </div>
                      </td>
                    </motion.tr>
                  ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination Footer */}
        {products.length > 0 && (
            <div className="p-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-50">
                <span className="text-xs text-slate-500 font-medium">نمایش {(currentPage - 1) * 10 + 1} تا {Math.min(currentPage * 10, totalItems)} از {totalItems} رکورد</span>
                <div className="join bg-white shadow-sm border border-slate-200 rounded-xl overflow-hidden">
                    <button className="join-item btn btn-sm btn-ghost disabled:bg-transparent px-4" disabled={currentPage === 1} onClick={() => setCurrentPage(p => p - 1)}>قبلی</button>
                    {Array.from({ length: totalPages }, (_, i) => (
                         <button key={i} className={clsx("join-item btn btn-sm w-10", currentPage === i + 1 ? "btn-primary text-white" : "btn-ghost text-slate-600")} onClick={() => setCurrentPage(i + 1)}>{i + 1}</button>
                    ))}
                    <button className="join-item btn btn-sm btn-ghost disabled:bg-transparent px-4" disabled={currentPage === totalPages} onClick={() => setCurrentPage(p => p + 1)}>بعدی</button>
                </div>
            </div>
        )}
      </div>

      <BulkActionsBar selectedCount={selectedIds.length} onClear={() => setSelectedIds([])} onDelete={handleBulkDelete} onStatusChange={handleBulkStatus} />
    </div>
  );
};

export default ProductListPage;