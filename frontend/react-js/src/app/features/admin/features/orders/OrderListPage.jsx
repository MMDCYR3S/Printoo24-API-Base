import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, Filter, Eye, Trash2, ShoppingCart, 
  Calendar, MoreVertical, FileText, ArrowUp, ArrowDown, CheckSquare, X
} from 'lucide-react';
import { useAdminOrders } from '../../hooks/useAdminOrders';
import { formatPrice } from '../../..../../utils/formatPrice';
import OrderStatusBadge from './components/OrderStatusBadge';
import BulkActionsBar from '../users/components/BulkActionsBar'; // استفاده مجدد از کامپوننت قبلی

const OrderListPage = () => {
  const navigate = useNavigate();
  const [selectedIds, setSelectedIds] = useState([]);
  
  const {
    orders,
    totalCount,
    totalPages,
    currentPage,
    setCurrentPage,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    sortConfig,
    handleSort,
    isLoading,
    deleteMutation,
    bulkDeleteMutation
  } = useAdminOrders();

  // --- Selection Logic ---
  const handleToggleAll = () => {
    if (selectedIds.length === orders.length) setSelectedIds([]);
    else setSelectedIds(orders.map(o => o.id));
  };

  const handleToggleOne = (id) => {
    if (selectedIds.includes(id)) setSelectedIds(prev => prev.filter(i => i !== id));
    else setSelectedIds(prev => [...prev, id]);
  };

  const handleDelete = (id) => {
    if (confirm('آیا از حذف این سفارش مطمئن هستید؟ این عملیات غیرقابل بازگشت است.')) {
      deleteMutation.mutate(id);
    }
  };

  const handleBulkDelete = () => {
    if (confirm(`آیا مطمئن هستید که می‌خواهید ${selectedIds.length} سفارش را حذف کنید؟`)) {
      bulkDeleteMutation.mutate(selectedIds, {
        onSuccess: () => setSelectedIds([])
      });
    }
  };

  // --- UI Helpers ---
  const SortIcon = ({ colKey }) => {
    if (sortConfig.key !== colKey) return <ArrowUp size={14} className="opacity-0 group-hover:opacity-30 transition-opacity" />;
    return sortConfig.direction === 'asc' 
      ? <ArrowUp size={14} className="text-primary" /> 
      : <ArrowDown size={14} className="text-primary" />;
  };

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
      <span className="loading loading-spinner loading-lg text-primary"></span>
      <p className="text-slate-400 animate-pulse">در حال دریافت لیست سفارشات...</p>
    </div>
  );

  return (
    <div className="p-6 space-y-6 pb-24">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-800 flex items-center gap-2">
            <ShoppingCart className="text-primary" />
            مدیریت سفارشات
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            <span className="font-bold text-slate-800">{totalCount}</span> سفارش ثبت شده
          </p>
        </div>
        <button 
          onClick={() => navigate('/admin/orders/create')} 
          className="btn btn-primary gap-2 shadow-lg shadow-primary/20"
        >
          <FileText size={18} />
          ثبت سفارش دستی
        </button>
      </div>

      {/* Filters Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm flex flex-col lg:flex-row gap-4 justify-between items-center z-20 relative">
        {/* Search */}
        <div className="relative w-full lg:w-96">
          <input 
            type="text" 
            placeholder="جستجو (نام کاربر، شناسه سفارش...)" 
            className="input input-bordered w-full pl-10 bg-slate-50 focus:bg-white transition-colors"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
        </div>

        {/* Filters */}
        <div className="flex w-full lg:w-auto gap-3">
          <select 
            className="select select-bordered w-full lg:w-48"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">همه وضعیت‌ها</option>
            <option value="Pending">در انتظار</option>
            <option value="Processing">در حال پردازش</option>
            <option value="Completed">تکمیل شده</option>
            <option value="Canceled">لغو شده</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden min-h-[400px]">
        <div className="overflow-x-auto">
          <table className="table w-full">
            <thead className="bg-slate-50/80 text-slate-500 font-semibold text-xs uppercase tracking-wider backdrop-blur-sm sticky top-0 z-10">
              <tr>
                <th className="w-12">
                  <label>
                    <input 
                      type="checkbox" 
                      className="checkbox checkbox-sm checkbox-primary rounded"
                      checked={orders.length > 0 && selectedIds.length === orders.length}
                      onChange={handleToggleAll}
                    />
                  </label>
                </th>
                <th onClick={() => handleSort('id')} className="cursor-pointer group hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-2">شناسه <SortIcon colKey="id"/></div>
                </th>
                <th onClick={() => handleSort('username')} className="cursor-pointer group hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-2">مشتری <SortIcon colKey="username"/></div>
                </th>
                <th className="text-center">وضعیت</th>
                <th onClick={() => handleSort('total_price')} className="cursor-pointer group hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-2">مبلغ کل <SortIcon colKey="total_price"/></div>
                </th>
                <th className="text-center">اقلام</th>
                <th onClick={() => handleSort('created_at')} className="cursor-pointer group hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-2">تاریخ ثبت <SortIcon colKey="created_at"/></div>
                </th>
                <th className="text-left w-20">عملیات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {orders.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-20 text-slate-400">
                    <div className="flex flex-col items-center gap-3">
                       <ShoppingCart size={48} className="opacity-20" />
                       <span>سفارشی یافت نشد</span>
                    </div>
                  </td>
                </tr>
              ) : (
                orders.map((order) => (
                  <tr key={order.id} className="hover:bg-slate-50/80 transition-colors group">
                    <th>
                      <label>
                        <input 
                          type="checkbox" 
                          className="checkbox checkbox-sm checkbox-primary rounded"
                          checked={selectedIds.includes(order.id)}
                          onChange={() => handleToggleOne(order.id)}
                        />
                      </label>
                    </th>
                    <td className="font-mono text-xs font-bold text-slate-600">
                      #{order.id}
                    </td>
                    <td>
                      <div className="flex flex-col">
                        <span className="font-bold text-slate-700">{order.username}</span>
                        {/* اینجا می‌توان user_info را اگر آبجکت بود تجزیه کرد */}
                      </div>
                    </td>
                    <td className="text-center">
                      <OrderStatusBadge status={order.status_name} />
                    </td>
                    <td>
                      <div className="font-bold text-emerald-600 dir-ltr text-right">
                        {formatPrice(order.total_price)} <span className="text-[10px] text-slate-400">IQD</span>
                      </div>
                    </td>
                    <td className="text-center">
                      <div className="badge badge-ghost badge-sm font-mono">
                        {order.items_count}
                      </div>
                    </td>
                    <td className="text-xs text-slate-500 font-mono">
                      {new Date(order.created_at).toLocaleDateString('fa-IR')}
                      <br/>
                      <span className="opacity-50">{new Date(order.created_at).toLocaleTimeString('fa-IR', {hour: '2-digit', minute:'2-digit'})}</span>
                    </td>
                    <td>
                      <div className="flex items-center justify-end gap-2">
                         <button 
                           onClick={() => navigate(`/admin/orders/${order.id}`)}
                           className="btn btn-square btn-ghost btn-sm text-primary hover:bg-primary/10" 
                           title="مشاهده جزئیات"
                         >
                           <Eye size={16} />
                         </button>
                         <button 
                           onClick={() => handleDelete(order.id)}
                           className="btn btn-square btn-ghost btn-sm text-error hover:bg-error/10" 
                           title="حذف"
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

        {/* Pagination Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
          <span className="text-xs text-slate-400">
            صفحه {currentPage} از {totalPages}
          </span>
          <div className="join bg-white shadow-sm">
            <button 
              className="join-item btn btn-sm btn-ghost" 
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(p => p - 1)}
            >
              قبلی
            </button>
            <button className="join-item btn btn-sm btn-disabled bg-white text-primary font-bold opacity-100">
              {currentPage}
            </button>
            <button 
              className="join-item btn btn-sm btn-ghost"
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage(p => p + 1)}
            >
              بعدی
            </button>
          </div>
        </div>
      </div>

      {/* Bulk Actions Floating Bar */}
      {/* چون قبلاً در Customers ساختیم، اینجا هم استفاده می‌کنیم ولی فقط برای Delete */}
      <BulkActionsBar 
        selectedCount={selectedIds.length}
        onClear={() => setSelectedIds([])}
        onDelete={handleBulkDelete}
        // اگر API تغییر وضعیت گروهی هم داشتی اینجا پاس بده
        onStatusChange={() => { alert('تغییر وضعیت گروهی سفارشات هنوز پیاده‌سازی نشده') }} 
      />
    </div>
  );
};

export default OrderListPage;