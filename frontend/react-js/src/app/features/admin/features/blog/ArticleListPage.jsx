import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Plus, Edit, Trash2, Send, CheckCircle, Clock, Archive, ArrowUp, ArrowDown } from 'lucide-react';
import clsx from 'clsx';
import { useAdminArticles } from './hooks/useAdminArticles';
import ArticleFilters from './components/ArticleFilters';
import ArticleBulkActionsBar from './components/ArticleBulkActionsBar';

const ArticleListPage = () => {
  const {
    articles,
    totalItems, totalPages, currentPage, setCurrentPage,
    searchQuery, setSearchQuery,
    statusFilter, setStatusFilter,
    sortConfig, handleSort,
    isLoading, refetch,
    deleteMutation, bulkDeleteMutation, bulkStatusMutation, publishMutation
  } = useAdminArticles();

  const [selectedIds, setSelectedIds] = useState([]);

  const handleSelectAll = (e) => {
    setSelectedIds(e.target.checked ? articles.map(a => a.id) : []);
  };

  const handleSelectOne = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const handleDelete = (id) => {
    if (window.confirm('آیا از حذف این مقاله مطمئن هستید؟')) {
      deleteMutation.mutate(id);
    }
  };

  const handleBulkDelete = () => {
    if (window.confirm(`حذف ${selectedIds.length} مقاله؟`)) {
      bulkDeleteMutation.mutate(selectedIds, { onSuccess: () => setSelectedIds([]) });
    }
  };

  const handleBulkStatus = (status) => {
    bulkStatusMutation.mutate({ ids: selectedIds, status }, { onSuccess: () => setSelectedIds([]) });
  };

  const getStatusBadge = (status) => {
    switch(status) {
      case 'published': return <span className="badge bg-emerald-50 text-emerald-600 border-0 gap-1"><CheckCircle size={12}/> منتشر شده</span>;
      case 'draft': return <span className="badge bg-slate-100 text-slate-500 border-0 gap-1"><Clock size={12}/> پیش‌نویس</span>;
      case 'archived': return <span className="badge bg-amber-50 text-amber-600 border-0 gap-1"><Archive size={12}/> بایگانی</span>;
      default: return null;
    }
  };

  const ThSortable = ({ label, sortKey, className }) => (
    <th 
      onClick={() => handleSort(sortKey)}
      className={clsx("cursor-pointer hover:bg-slate-100 transition-colors select-none py-4", className)}
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
      
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-800 flex items-center gap-3">
            <span className="p-3 bg-primary/10 text-primary rounded-2xl"><FileText size={28} /></span>
            مدیریت مقالات بلاگ
          </h1>
          <p className="text-slate-500 mt-2 text-sm">مدیریت، نوشتن و انتشار مقالات آموزشی</p>
        </div>
        <Link to="new" className="btn btn-primary px-6 shadow-lg shadow-primary/30 h-12 rounded-xl">
          <Plus size={20} /> نوشتن مقاله جدید
        </Link>
      </div>

      <ArticleFilters 
        searchQuery={searchQuery} setSearchQuery={setSearchQuery}
        statusFilter={statusFilter} setStatusFilter={setStatusFilter}
        onRefresh={() => refetch()}
      />

      <div className="bg-white rounded-[2rem] border border-slate-100 shadow-xl shadow-slate-200/40 overflow-hidden min-h-[400px]">
        {isLoading ? (
            <div className="flex justify-center items-center h-64"><span className="loading loading-spinner text-primary"></span></div>
        ) : (
            <>
              <div className="overflow-x-auto">
                  <table className="table w-full">
                      <thead className="bg-slate-50/80 text-xs uppercase font-bold tracking-wider border-b border-slate-100 text-slate-500 backdrop-blur-md">
                          <tr>
                              <th className="w-16 text-center">
                                  <input type="checkbox" className="checkbox checkbox-sm checkbox-primary rounded-md" 
                                      checked={articles.length > 0 && selectedIds.length === articles.length} 
                                      onChange={handleSelectAll} 
                                  />
                              </th>
                              <th className="w-20 text-center">تصویر</th>
                              <ThSortable label="عنوان مقاله" sortKey="title" />
                              <ThSortable label="دسته‌بندی" sortKey="category_name" />
                              <ThSortable label="تاریخ انتشار" sortKey="published_at" />
                              <ThSortable label="وضعیت" sortKey="status" className="text-center" />
                              <th className="text-left pl-6">عملیات</th>
                          </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-50">
                          {articles.length === 0 ? (
                              <tr><td colSpan="7" className="text-center py-12 text-slate-400">هیچ مقاله‌ای یافت نشد.</td></tr>
                          ) : (
                              articles.map(article => (
                                  <tr key={article.id} className={clsx("hover:bg-blue-50/30 transition-colors group", selectedIds.includes(article.id) && "bg-blue-50/60")}>
                                      <th className="text-center">
                                          <input type="checkbox" className="checkbox checkbox-sm checkbox-primary rounded-md"
                                              checked={selectedIds.includes(article.id)}
                                              onChange={() => handleSelectOne(article.id)}
                                          />
                                      </th>
                                      <td className="text-center">
                                        <div className="avatar">
                                          <div className="w-12 h-12 rounded-xl ring-1 ring-slate-100 bg-white">
                                            {article.image ? <img src={article.image} alt={article.title} className="object-cover"/> : <div className="w-full h-full bg-slate-50 flex items-center justify-center text-slate-300"><FileText size={20}/></div>}
                                          </div>
                                        </div>
                                      </td>
                                      <td>
                                        <Link to={`edit/${article.id}`} className="font-bold text-slate-700 hover:text-primary transition-colors text-sm">
                                          {article.title}
                                        </Link>
                                        <div className="text-xs text-slate-400 mt-1 line-clamp-1 max-w-xs">{article.summary}</div>
                                      </td>
                                      <td><span className="badge badge-ghost text-xs font-medium">{article.category_name}</span></td>
                                      <td className="text-xs text-slate-500 font-mono" dir="ltr">
                                          {article.published_at ? new Date(article.published_at).toLocaleDateString('fa-IR') : 'ندارد'}
                                      </td>
                                      <td className="text-center">{getStatusBadge(article.status)}</td>
                                      <td>
                                        <div className="flex justify-end items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                                            {article.status !== 'published' && (
                                              <button 
                                                  onClick={() => publishMutation.mutate(article.id)}
                                                  className="btn btn-sm btn-ghost btn-square text-emerald-500 hover:bg-emerald-50 tooltip tooltip-top"
                                                  data-tip="انتشار سریع"
                                              >
                                                  <Send size={16} />
                                              </button>
                                            )}
                                            <Link 
                                                to={`edit/${article.id}`}
                                                className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-blue-600 tooltip tooltip-top"
                                                data-tip="ویرایش"
                                            >
                                                <Edit size={16} />
                                            </Link>
                                            <button 
                                                onClick={() => handleDelete(article.id)}
                                                className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-red-500 tooltip tooltip-top"
                                                data-tip="حذف"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                      </td>
                                  </tr>
                              ))
                          )}
                      </tbody>
                  </table>
              </div>

              {/* Pagination Controls */}
              {totalPages > 1 && (
                <div className="p-4 border-t border-slate-100 flex items-center justify-between bg-slate-50/50">
                  <span className="text-sm text-slate-500">
                    نمایش {(currentPage - 1) * 10 + 1} تا {Math.min(currentPage * 10, totalItems)} از {totalItems} مقاله
                  </span>
                  <div className="join border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                    <button 
                      className="join-item btn btn-sm bg-white hover:bg-slate-50 border-0" 
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                    >
                      قبلی
                    </button>
                    <button className="join-item btn btn-sm bg-white border-0 cursor-default px-4 font-mono">
                      {currentPage} / {totalPages}
                    </button>
                    <button 
                      className="join-item btn btn-sm bg-white hover:bg-slate-50 border-0" 
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                    >
                      بعدی
                    </button>
                  </div>
                </div>
              )}
            </>
        )}
      </div>

      <ArticleBulkActionsBar 
        selectedCount={selectedIds.length}
        onClear={() => setSelectedIds([])}
        onDelete={handleBulkDelete}
        onStatusChange={handleBulkStatus}
      />
    </div>
  );
};

export default ArticleListPage;