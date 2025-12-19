// src/app/features/admin/ProductListPage.jsx
import React from 'react';
import { 
  Search, Filter, MoreVertical, Edit, Trash2, Eye, 
  ChevronDown, ArrowUp, ArrowDown, Package, Plus 
} from 'lucide-react';
import { useAdminProducts } from '../../hooks/useAdminProducts';

const ProductListPage = () => {
  const {
    products,
    totalItems,
    totalPages,
    currentPage,
    setCurrentPage,
    searchQuery,
    setSearchQuery,
    sortConfig,
    handleSort,
    isLoading,
  } = useAdminProducts();

  // فرمتر قیمت
  const formatPrice = (price) => 
    new Intl.NumberFormat('fa-IQ').format(parseFloat(price));

  // کامپوننت کمکی برای هدر جدول (جهت سورت)
  const SortableHeader = ({ label, sortKey }) => (
    <th 
      className="cursor-pointer hover:bg-base-200 transition-colors select-none group"
      onClick={() => handleSort(sortKey)}
    >
      <div className="flex items-center gap-2">
        {label}
        <span className={`opacity-0 group-hover:opacity-50 ${sortConfig.key === sortKey ? '!opacity-100 text-primary' : ''}`}>
          {sortConfig.key === sortKey && sortConfig.direction === 'asc' ? <ArrowUp size={14}/> : <ArrowDown size={14}/>}
        </span>
      </div>
    </th>
  );

  return (
    <div className="p-4 md:p-6 min-h-screen bg-base-100/50 space-y-6">
      
      {/* --- هدر صفحه --- */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-base-content flex items-center gap-2">
            <Package className="text-primary" />
            مدیریت محصولات
          </h1>
          <p className="text-sm text-base-content/60 mt-1">
            لیست کامل محصولات چاپی، ویرایش قیمت‌ها و موجودی
          </p>
        </div>
        <button className="btn btn-primary shadow-lg shadow-primary/30 text-white gap-2">
          <Plus size={18} />
          افزودن محصول جدید
        </button>
      </div>

      {/* --- باکس ابزارها (Search & Filter) --- */}
      <div className="bg-white p-4 rounded-2xl shadow-sm border border-base-200 flex flex-col md:flex-row gap-4 items-center justify-between sticky top-2 z-20 backdrop-blur-xl bg-white/90">
        
        {/* جستجو */}
        <div className="relative w-full md:w-96">
          <input
            type="text"
            placeholder="جستجو نام، کد محصول یا دسته‌بندی..."
            className="input input-bordered w-full pl-10 bg-gray-50 focus:bg-white transition-all"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1); // برگشت به صفحه اول بعد از سرچ
            }}
          />
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-base-content/40" size={18} />
        </div>

        {/* خلاصه وضعیت */}
        <div className="text-xs font-medium text-base-content/50 bg-base-100 px-3 py-2 rounded-lg">
          نمایش {products.length} از {totalItems} محصول
        </div>
      </div>

      {/* --- جدول دیتا --- */}
      <div className="bg-white rounded-2xl shadow-xl shadow-base-200/50 border border-base-200 overflow-hidden flex flex-col min-h-[500px]">
        {isLoading ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-3">
             <span className="loading loading-spinner loading-lg text-primary"></span>
             <span className="text-sm text-gray-400">در حال دریافت لیست محصولات...</span>
          </div>
        ) : (
          <div className="overflow-x-auto flex-1">
            <table className="table table-pin-rows table-md w-full">
              {/* هدر */}
              <thead>
                <tr className="bg-base-100/50 text-base-content/70">
                  <SortableHeader label="#" sortKey="id" />
                  <SortableHeader label="نام محصول" sortKey="name" />
                  <SortableHeader label="کد محصول (SKU)" sortKey="code" />
                  <SortableHeader label="قیمت پایه" sortKey="price" />
                  <th className="text-center">وضعیت</th>
                  <th className="text-center w-24">عملیات</th>
                </tr>
              </thead>
              
              {/* بدنه */}
              <tbody>
                {products.length > 0 ? (
                  products.map((product) => (
                    <tr key={product.id} className="hover:bg-gray-50 transition-colors group">
                      <td className="font-mono text-xs opacity-50">{product.id}</td>
                      
                      <td>
                        <div className="flex flex-col">
                          <span className="font-bold text-base-content group-hover:text-primary transition-colors">
                            {product.name}
                          </span>
                          <span className="text-[10px] text-gray-400">slug: {product.slug}</span>
                        </div>
                      </td>

                      <td>
                        <div className="badge badge-ghost badge-sm font-mono text-xs gap-1">
                          <span className="opacity-50">#</span>{product.code.split('-').pop()}
                        </div>
                      </td>

                      <td>
                        {parseFloat(product.price) > 0 ? (
                          <div className="font-bold text-emerald-600">
                            {formatPrice(product.price)} <span className="text-[10px]">IQD</span>
                          </div>
                        ) : (
                          <div className="badge badge-warning badge-outline text-xs">تماس بگیرید</div>
                        )}
                      </td>

                      <td className="text-center">
                        <label className="swap swap-rotate">
                          <input type="checkbox" checked={product.is_active} readOnly />
                          <span className="swap-on badge badge-success badge-xs gap-1 text-white shadow-success/40 shadow-md">
                            فعال
                          </span>
                          <span className="swap-off badge badge-error badge-xs gap-1 text-white">
                            غیرفعال
                          </span>
                        </label>
                      </td>

                      <td>
                        <div className="dropdown dropdown-left dropdown-bottom">
                          <button tabIndex={0} className="btn btn-ghost btn-sm btn-square text-gray-400 hover:text-primary hover:bg-primary/10">
                            <MoreVertical size={16} />
                          </button>
                          <ul tabIndex={0} className="dropdown-content z-[1] menu p-2 shadow-2xl bg-white rounded-xl w-48 border border-base-100">
                             <li>
                               <button className="text-xs font-medium hover:text-primary">
                                 <Eye size={14}/> مشاهده جزئیات
                               </button>
                             </li>
                             <li>
                               <button className="text-xs font-medium hover:text-warning">
                                 <Edit size={14}/> ویرایش محصول
                               </button>
                             </li>
                             <div className="divider my-1"></div>
                             <li>
                               <button className="text-xs font-medium text-error hover:bg-error/10">
                                 <Trash2 size={14}/> حذف محصول
                               </button>
                             </li>
                          </ul>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="h-64 text-center text-gray-400">
                      محصولی با این مشخصات یافت نشد :(
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* --- Pagination --- */}
        <div className="p-4 border-t border-base-200 bg-gray-50 flex items-center justify-between">
            <button 
              className="btn btn-sm btn-ghost"
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(p => p - 1)}
            >
              قبلی
            </button>
            
            <div className="join shadow-sm bg-white">
              {[...Array(totalPages)].map((_, i) => (
                <button
                  key={i}
                  className={`join-item btn btn-sm ${currentPage === i + 1 ? 'btn-primary text-white' : 'btn-ghost'}`}
                  onClick={() => setCurrentPage(i + 1)}
                >
                  {i + 1}
                </button>
              ))}
            </div>

            <button 
              className="btn btn-sm btn-ghost"
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage(p => p + 1)}
            >
              بعدی
            </button>
        </div>
      </div>
    </div>
  );
};

export default ProductListPage;