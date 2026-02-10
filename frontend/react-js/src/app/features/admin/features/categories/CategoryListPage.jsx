// src/app/features/admin/categories/CategoryListPage.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Layers, Plus, ArrowUp, ArrowDown, Grid, ListTree } from 'lucide-react';
import clsx from 'clsx';
import { useAdminCategories } from '../../hooks/useAdminCategories';
import CategoryFilters from './components/CategoryFilters';
import CategoryRow from './components/CategoryRow';      // کامپوننت درختی (تب ۱)
import SubCategoryTable from './components/SubCategoryTable'; // کامپوننت لیست زیردسته‌ها (تب ۲)
import BulkActionsBar from '../users/components/BulkActionsBar'; 

const CategoryListPage = () => {
  const [activeTab, setActiveTab] = useState('roots'); // 'roots' | 'subs'

  const {
    categories, // لیست والدها (درختی)
    isLoading,
    searchQuery, setSearchQuery,
    statusFilter, setStatusFilter,
    sortConfig, handleSort,
    deleteMutation,
    toggleStatusMutation,
    bulkDeleteMutation
  } = useAdminCategories();

  const [selectedIds, setSelectedIds] = useState([]);

  // --- هندلرهای انتخاب و حذف (مخصوص تب والدها) ---
  const handleSelectAll = (e) => {
    setSelectedIds(e.target.checked ? categories.map(c => c.id) : []);
  };

  const handleSelectOne = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const handleDelete = (id) => {
    if (window.confirm('آیا مطمئن هستید؟ حذف والد ممکن است باعث حذف فرزندان شود.')) {
      deleteMutation.mutate(id);
    }
  };

  const handleBulkDelete = () => {
    if (window.confirm(`حذف ${selectedIds.length} مورد؟`)) {
      bulkDeleteMutation.mutate(selectedIds, { onSuccess: () => setSelectedIds([]) });
    }
  };

  return (
    <div className="p-4 md:p-8 max-w-[1920px] mx-auto min-h-screen space-y-6 pb-32 animate-fade-in">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-800 flex items-center gap-3">
            <span className="p-3 bg-primary/10 text-primary rounded-2xl"><Layers size={28} /></span>
            مدیریت دسته‌بندی‌ها
          </h1>
          <p className="text-slate-500 mt-2 text-sm">مدیریت دسته‌های اصلی و زیرمجموعه‌ها</p>
        </div>
        
        <Link to="new" className="btn btn-primary px-6 shadow-lg shadow-primary/30 h-12">
          <Plus size={20} /> افزودن دسته جدید
        </Link>
      </div>

      {/* --- TABS (بازگردانده شد) --- */}
      <div role="tablist" className="tabs tabs-boxed bg-white p-1.5 rounded-2xl border border-slate-100 w-fit shadow-sm">
        <button 
            role="tab" 
            className={clsx("tab h-10 px-6 rounded-xl gap-2 transition-all font-bold text-sm", activeTab === 'roots' && "bg-primary text-white shadow-md")}
            onClick={() => setActiveTab('roots')}
        >
            <Grid size={16}/> دسته‌های اصلی (درختی)
        </button>
        <button 
            role="tab" 
            className={clsx("tab h-10 px-6 rounded-xl gap-2 transition-all font-bold text-sm", activeTab === 'subs' && "bg-primary text-white shadow-md")}
            onClick={() => setActiveTab('subs')}
        >
            <ListTree size={16}/> لیست کل زیردسته‌ها
        </button>
      </div>

      {/* --- محتوای تب ۱: دسته‌های اصلی (درختی) --- */}
      {activeTab === 'roots' && (
        <>
            {/* Filters */}
            <div className="sticky top-2 z-20">
                <CategoryFilters 
                    searchQuery={searchQuery} setSearchQuery={setSearchQuery}
                    statusFilter={statusFilter} setStatusFilter={setStatusFilter}
                    onRefresh={() => window.location.reload()}
                />
            </div>

            {/* Table */}
            <div className="bg-white rounded-[2rem] border border-slate-100 shadow-xl shadow-slate-200/40 overflow-hidden min-h-[400px]">
                {isLoading ? (
                    <div className="flex justify-center items-center h-64"><span className="loading loading-spinner text-primary"></span></div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="table w-full">
                            <thead className="bg-slate-50/80 text-xs uppercase font-bold tracking-wider border-b border-slate-100 text-slate-500">
                                <tr>
                                    <th className="w-12 text-center">
                                        <input type="checkbox" className="checkbox checkbox-sm checkbox-primary rounded-md" 
                                            checked={categories.length > 0 && selectedIds.length === categories.length} 
                                            onChange={handleSelectAll} 
                                        />
                                    </th>
                                    <th className="w-20">تصویر</th>
                                    <th onClick={() => handleSort('name')} className="cursor-pointer hover:bg-slate-100 transition-colors">
                                        نام دسته‌بندی 
                                        {sortConfig.key === 'name' && (sortConfig.direction === 'asc' ? <ArrowUp size={12} className="inline ml-1"/> : <ArrowDown size={12} className="inline ml-1"/>)}
                                    </th>
                                    <th>نامک (Slug)</th>
                                    <th className="text-center">وضعیت</th>
                                    <th className="text-left pl-6">عملیات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {categories.length === 0 ? (
                                    <tr><td colSpan="6" className="text-center py-12 text-slate-400">موردی یافت نشد.</td></tr>
                                ) : (
                                    categories.map(cat => (
                                        <CategoryRow 
                                            key={cat.id} 
                                            category={cat} 
                                            isSelected={selectedIds.includes(cat.id)}
                                            onSelect={handleSelectOne}
                                            onDelete={handleDelete}
                                            onToggleStatus={(ids, status) => toggleStatusMutation.mutate({ ids, active: status })}
                                        />
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Bulk Actions (فقط برای تب اصلی) */}
            <BulkActionsBar 
                selectedCount={selectedIds.length}
                onClear={() => setSelectedIds([])}
                onDelete={handleBulkDelete}
                onStatusChange={(status) => toggleStatusMutation.mutate({ ids: selectedIds, active: status }, { onSuccess: () => setSelectedIds([]) })}
            />
        </>
      )}

      {/* --- محتوای تب ۲: لیست زیردسته‌ها --- */}
      {activeTab === 'subs' && (
        <div className="animate-fade-in-up">
            {/* از همان کامپوننت SubCategoryTable که قبلا ساختیم و آکاردئونی است استفاده می‌کنیم */}
            <SubCategoryTable />
        </div>
      )}

    </div>
  );
};

export default CategoryListPage;