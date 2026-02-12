// src/app/features/admin/categories/CategoryListPage.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Layers, Plus, ListTree, Grid } from 'lucide-react';
import { useAdminCategories } from '../../hooks/useAdminCategories';
import CategoryFilters from './components/CategoryFilters';
import CategoryRow from './components/CategoryRow'; // جدول والدها (قبلی)
import SubCategoryTable from './components/SubCategoryTable'; // جدول جدید زیردسته‌ها
import clsx from 'clsx';

const CategoryListPage = () => {
  const [activeTab, setActiveTab] = useState('roots'); // 'roots' | 'subs'

  const {
    categories, // لیست والدها
    isLoading,
    searchQuery, setSearchQuery,
    deleteMutation,
    toggleStatusMutation
  } = useAdminCategories();

  return (
    <div className="p-6 max-w-[1920px] mx-auto min-h-screen pb-32 animate-fade-in space-y-6">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-800 flex items-center gap-3">
            <span className="p-2 bg-primary/10 text-primary rounded-xl"><Layers size={24} /></span>
            مدیریت دسته‌بندی‌ها
          </h1>
        </div>
        
        {/* دکمه ایجاد با مسیر صحیح */}
        <Link 
            to="/admin/categories/new" 
            className="btn btn-primary px-6 shadow-lg shadow-primary/30"
        >
          <Plus size={20} /> افزودن دسته جدید
        </Link>
      </div>

      {/* TABS */}
      <div role="tablist" className="tabs tabs-boxed bg-white p-1 rounded-xl border border-slate-100 w-fit">
        <button 
            role="tab" 
            className={clsx("tab h-10 px-6 rounded-lg gap-2 transition-all", activeTab === 'roots' && "bg-primary text-white shadow-md")}
            onClick={() => setActiveTab('roots')}
        >
            <Grid size={16}/> دسته‌های اصلی (والد)
        </button>
        <button 
            role="tab" 
            className={clsx("tab h-10 px-6 rounded-lg gap-2 transition-all", activeTab === 'subs' && "bg-primary text-white shadow-md")}
            onClick={() => setActiveTab('subs')}
        >
            <ListTree size={16}/> تمام زیردسته‌ها
        </button>
      </div>

      {/* Content based on Tab */}
      {activeTab === 'roots' ? (
        <>
            {/* فیلتر فقط برای والدها فعلا */}
            <div className="sticky top-0 z-10 bg-slate-50/80 backdrop-blur pb-2">
                <CategoryFilters searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
            </div>

            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                {isLoading ? (
                    <div className="flex justify-center p-10"><span className="loading loading-spinner text-primary"></span></div>
                ) : (
                    <table className="table w-full">
                        <thead className="bg-slate-50 text-xs uppercase font-bold text-slate-500">
                            <tr>
                                <th className="w-12 text-center">#</th>
                                <th className="w-20">تصویر</th>
                                <th>نام دسته (والد)</th>
                                <th>نامک</th>
                                <th className="text-center">وضعیت</th>
                                <th className="text-left pl-6">عملیات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {categories.map((cat) => (
                                <CategoryRow 
                                    key={cat.id} 
                                    category={cat}
                                    isSelected={false} // فعلا غیرفعال
                                    onSelect={() => {}}
                                    onDelete={(id) => deleteMutation.mutate(id)}
                                    onToggleStatus={(ids, s) => toggleStatusMutation.mutate({ids, active: s})}
                                />
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </>
      ) : (
        /* تب زیردسته‌ها (کامپوننت جدا) */
        <SubCategoryTable />
      )}

    </div>
  );
};

export default CategoryListPage;