import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { PlaySquare, Plus, Edit, Trash2, ArrowUp, ArrowDown, CheckCircle2, XCircle, Search, Filter, RefreshCw, X, CheckCircle, Ban } from 'lucide-react';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';
import { useAdminTutorials } from './hooks/useAdminTutorials';

const TutorialListPage = () => {
  const {
    tutorials, totalItems, totalPages, currentPage, setCurrentPage,
    searchQuery, setSearchQuery, statusFilter, setStatusFilter,
    sortConfig, handleSort, isLoading, refetch,
    deleteMutation, bulkDeleteMutation, bulkStatusMutation
  } = useAdminTutorials();

  const [selectedIds, setSelectedIds] = useState([]);

  const handleSelectAll = (e) => setSelectedIds(e.target.checked ? tutorials.map(t => t.id) : []);
  const handleSelectOne = (id) => setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);

  const handleDelete = (id) => {
    if (window.confirm('آیا از حذف این آموزش مطمئن هستید؟')) deleteMutation.mutate(id);
  };
  const handleBulkDelete = () => {
    if (window.confirm(`حذف ${selectedIds.length} آموزش؟`)) bulkDeleteMutation.mutate(selectedIds, { onSuccess: () => setSelectedIds([]) });
  };
  const handleBulkStatus = (is_active) => {
    bulkStatusMutation.mutate({ ids: selectedIds, is_active }, { onSuccess: () => setSelectedIds([]) });
  };

  const ThSortable = ({ label, sortKey, className }) => (
    <th onClick={() => handleSort(sortKey)} className={clsx("cursor-pointer hover:bg-slate-100 transition-colors select-none py-4", className)}>
      <div className="flex items-center gap-2 text-slate-600">
        {label}
        {sortConfig.key === sortKey && (sortConfig.direction === 'asc' ? <ArrowUp size={14} className="text-primary"/> : <ArrowDown size={14} className="text-primary"/>)}
      </div>
    </th>
  );

  return (
    <div className="p-4 md:p-8 max-w-[1920px] mx-auto min-h-screen space-y-6 pb-32 animate-fade-in">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-800 flex items-center gap-3">
            <span className="p-3 bg-red-100 text-red-600 rounded-2xl"><PlaySquare size={28} /></span>
            مدیریت آموزش‌های ویدیویی
          </h1>
          <p className="text-slate-500 mt-2 text-sm">افزودن و مدیریت ویدیوهای یوتیوب برای سایت</p>
        </div>
        <Link to="new" className="btn btn-error text-white px-6 shadow-lg shadow-red-500/30 h-12 rounded-xl border-0">
          <Plus size={20} /> افزودن آموزش جدید
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white/80 backdrop-blur-xl p-4 rounded-2xl border border-slate-100 shadow-lg shadow-slate-200/20 flex flex-col md:flex-row gap-4 items-center justify-between z-20 relative">
        <div className="relative w-full md:w-96 group">
          <Search size={18} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-primary transition-colors" />
          <input
            type="text" placeholder="جستجو در عنوان آموزش‌ها..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
            className="input w-full bg-slate-50 border-slate-200 focus:border-primary focus:ring-2 focus:ring-primary/20 rounded-xl pr-12 text-sm"
          />
        </div>
        <div className="flex items-center gap-3 w-full md:w-auto">
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="select w-full md:w-48 bg-slate-50 border-slate-200 focus:border-primary rounded-xl text-sm">
            <option value="all">همه وضعیت‌ها</option>
            <option value="active">فعال</option>
            <option value="inactive">غیرفعال</option>
          </select>
          <button onClick={() => refetch()} className="btn btn-square bg-slate-50 border-slate-200 text-slate-500 hover:bg-white hover:text-primary transition-all rounded-xl">
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-[2rem] border border-slate-100 shadow-xl shadow-slate-200/40 overflow-hidden min-h-[400px]">
        {isLoading ? (
            <div className="flex justify-center items-center h-64"><span className="loading loading-spinner text-red-500"></span></div>
        ) : (
            <>
              <div className="overflow-x-auto">
                  <table className="table w-full">
                      <thead className="bg-slate-50/80 text-xs uppercase font-bold tracking-wider border-b border-slate-100 text-slate-500">
                          <tr>
                              <th className="w-16 text-center"><input type="checkbox" className="checkbox checkbox-sm rounded-md" checked={tutorials.length > 0 && selectedIds.length === tutorials.length} onChange={handleSelectAll} /></th>
                              <th className="w-24 text-center">کاور ویدیو</th>
                              <ThSortable label="عنوان آموزش" sortKey="title" />
                              <ThSortable label="تاریخ ثبت" sortKey="created_at" />
                              <ThSortable label="وضعیت" sortKey="is_active" className="text-center" />
                              <th className="text-left pl-6">عملیات</th>
                          </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-50">
                          {tutorials.length === 0 ? (
                              <tr><td colSpan="6" className="text-center py-12 text-slate-400">هیچ آموزشی یافت نشد.</td></tr>
                          ) : (
                              tutorials.map(tut => (
                                  <tr key={tut.id} className={clsx("hover:bg-red-50/30 transition-colors group", selectedIds.includes(tut.id) && "bg-red-50/60")}>
                                      <th className="text-center"><input type="checkbox" className="checkbox checkbox-sm rounded-md" checked={selectedIds.includes(tut.id)} onChange={() => handleSelectOne(tut.id)} /></th>
                                      <td className="text-center">
                                          <div className="w-20 h-14 rounded-lg overflow-hidden bg-slate-100 relative">
                                              {tut.thumbnail ? <img src={tut.thumbnail} alt={tut.title} className="w-full h-full object-cover"/> : <div className="absolute inset-0 flex items-center justify-center text-slate-300"><PlaySquare size={20}/></div>}
                                          </div>
                                      </td>
                                      <td>
                                          <Link to={`edit/${tut.id}`} className="font-bold text-slate-700 hover:text-red-600 transition-colors">{tut.title}</Link>
                                          <div className="text-xs text-slate-400 font-mono mt-1">/{tut.slug}</div>
                                      </td>
                                      <td className="text-xs text-slate-500 font-mono" dir="ltr">
                                          {tut.created_at ? new Date(tut.created_at).toLocaleDateString('fa-IR') : '-'}
                                      </td>
                                      <td className="text-center">
                                          {tut.is_active 
                                            ? <span className="badge bg-emerald-50 text-emerald-600 border-0 gap-1"><CheckCircle2 size={12}/> فعال</span>
                                            : <span className="badge bg-slate-100 text-slate-500 border-0 gap-1"><XCircle size={12}/> غیرفعال</span>
                                          }
                                      </td>
                                      <td>
                                        <div className="flex justify-end items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                                            <Link to={`edit/${tut.id}`} className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-blue-600"><Edit size={16} /></Link>
                                            <button onClick={() => handleDelete(tut.id)} className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-red-500"><Trash2 size={16} /></button>
                                        </div>
                                      </td>
                                  </tr>
                              ))
                          )}
                      </tbody>
                  </table>
              </div>
              {/* Pagination */}
              {totalPages > 1 && (
                <div className="p-4 border-t border-slate-100 flex items-center justify-between bg-slate-50/50">
                  <span className="text-sm text-slate-500">نمایش {(currentPage - 1) * itemsPerPage + 1} تا {Math.min(currentPage * itemsPerPage, totalItems)} از {totalItems}</span>
                  <div className="join border border-slate-200 rounded-xl overflow-hidden">
                    <button className="join-item btn btn-sm bg-white border-0" onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1}>قبلی</button>
                    <button className="join-item btn btn-sm bg-white border-0 cursor-default px-4 font-mono">{currentPage} / {totalPages}</button>
                    <button className="join-item btn btn-sm bg-white border-0" onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages}>بعدی</button>
                  </div>
                </div>
              )}
            </>
        )}
      </div>

      {/* Bulk Actions Bar */}
      <AnimatePresence>
        {selectedIds.length > 0 && (
          <motion.div initial={{ y: 100, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 100, opacity: 0 }} className="fixed bottom-8 left-1/2 -translate-x-1/2 z-[50] flex items-center gap-4 bg-slate-900 text-white pl-3 pr-6 py-3 rounded-2xl shadow-2xl backdrop-blur-md">
            <div className="flex items-center gap-3 border-l border-white/10 pl-4">
              <div className="badge badge-error text-white font-bold">{selectedIds.length}</div><span className="text-sm font-medium">مورد انتخاب شد</span>
            </div>
            <div className="flex items-center gap-1">
              <button onClick={() => handleBulkStatus(true)} className="btn btn-ghost btn-sm text-emerald-400 hover:bg-white/10 gap-2 font-normal"><CheckCircle size={18}/> فعال‌سازی</button>
              <button onClick={() => handleBulkStatus(false)} className="btn btn-ghost btn-sm text-amber-400 hover:bg-white/10 gap-2 font-normal"><Ban size={18}/> غیرفعال‌سازی</button>
              <button onClick={handleBulkDelete} className="btn btn-ghost btn-sm text-red-400 hover:bg-red-500/20 gap-2 font-normal"><Trash2 size={18}/> حذف</button>
            </div>
            <button onClick={() => setSelectedIds([])} className="btn btn-circle btn-xs btn-ghost text-white/40 hover:text-white mr-2"><X size={16} /></button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default TutorialListPage;