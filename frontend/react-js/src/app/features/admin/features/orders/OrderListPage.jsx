import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, Eye, Trash2, ShoppingCart, FileText, 
  Calendar as CalendarIcon, FilterX, RefreshCw
} from 'lucide-react';
import { useAdminOrders } from '../../hooks/useAdminOrders';
import { useOrderStatuses } from '../../hooks/useOrderStatuses';
import { formatPrice } from '../../utils/formatPrice';
import BulkActionsBar from '../users/components/BulkActionsBar';

const STATUS_STYLES = {
  PENDING_REVIEW: { badge: 'bg-blue-50 text-blue-700 ring-1 ring-blue-200/60',          dot: 'bg-blue-500'    },
  DESIGNING:      { badge: 'bg-purple-50 text-purple-700 ring-1 ring-purple-200/60',    dot: 'bg-purple-500'  },
  PRINTING:       { badge: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200/60',       dot: 'bg-amber-500'   },
  SHIPPED:        { badge: 'bg-sky-50 text-sky-700 ring-1 ring-sky-200/60',             dot: 'bg-sky-500'     },
  DELIVERED:      { badge: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200/60', dot: 'bg-emerald-500' },
  CANCELED:       { badge: 'bg-red-50 text-red-600 ring-1 ring-red-200/60',             dot: 'bg-red-500'     },
};

const getStatusStyle = (code) =>
  STATUS_STYLES[code] ?? { badge: 'bg-slate-100 text-slate-500', dot: 'bg-slate-400' };

const OrderListPage = () => {
  const navigate = useNavigate();
  const [selectedIds, setSelectedIds] = useState([]);
  
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [selectedOrderForStatus, setSelectedOrderForStatus] = useState(null);
  const [newStatusDesc, setNewStatusDesc] = useState('');
  const [newStatusCode, setNewStatusCode] = useState('');

  const { statuses } = useOrderStatuses();
  const {
    orders, totalCount, totalPages, currentPage, setCurrentPage,
    searchQuery, setSearchQuery, statusIdFilter, setStatusIdFilter,
    dateFilter, setDateFilter, isLoading, isFetching,
    deleteMutation, bulkDeleteMutation, changeStatusMutation
  } = useAdminOrders();

  const handleToggleAll = () => {
    if (selectedIds.length === orders.length && orders.length > 0) setSelectedIds([]);
    else setSelectedIds(orders.map(o => o.id));
  };

  const handleToggleOne = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const handleBulkDelete = () => {
    if (confirm(`آیا مطمئن هستید که می‌خواهید ${selectedIds.length} سفارش را حذف کنید؟`)) {
      bulkDeleteMutation.mutate(selectedIds, {
        onSuccess: () => setSelectedIds([])
      });
    }
  };

  const openStatusModal = (order, targetStatusCode) => {
    setSelectedOrderForStatus(order);
    setNewStatusCode(targetStatusCode);
    setNewStatusDesc('');
    setStatusModalOpen(true);
  };

  const submitStatusChange = () => {
    if (!selectedOrderForStatus || !newStatusCode) return;
    changeStatusMutation.mutate(
      { id: selectedOrderForStatus.id, data: { status_code: newStatusCode, description: newStatusDesc } },
      { onSuccess: () => setStatusModalOpen(false) }
    );
  };

  const resetFilters = () => {
    setSearchQuery('');
    setStatusIdFilter('all');
    setDateFilter('');
    setCurrentPage(1);
  };

  return (
    <div className="p-6 space-y-6 pb-24 animate-fade-in relative">
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-800 flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-xl">
              <ShoppingCart className="text-primary" size={24} />
            </div>
            مدیریت سفارشات
          </h1>
          <p className="text-sm text-slate-500 mt-2 flex items-center gap-2">
            کل سفارشات یافت شده: <span className="font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded">{totalCount}</span>
            {isFetching && <RefreshCw size={14} className="animate-spin text-primary" />}
          </p>
        </div>
        <button 
          onClick={() => navigate('/admin/orders/create')} 
          className="btn btn-primary gap-2 shadow-xl shadow-primary/20 rounded-xl"
        >
          <FileText size={18} /> ثبت سفارش دستی
        </button>
      </div>

      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col gap-4">
        <div className="flex overflow-x-auto hide-scrollbar gap-2 pb-2 border-b border-slate-100">
          <button 
            onClick={() => { setStatusIdFilter('all'); setCurrentPage(1); }}
            className={`btn btn-sm rounded-lg px-6 transition-all ${statusIdFilter === 'all' ? 'bg-slate-800 text-white hover:bg-slate-700' : 'btn-ghost text-slate-500 hover:bg-slate-100'}`}
          >
            همه سفارشات
          </button>
          {statuses?.map(status => (
            <button 
              key={status.id}
              onClick={() => { setStatusIdFilter(String(status.internal_code)); setCurrentPage(1); }}
              className={`btn btn-sm rounded-lg px-6 whitespace-nowrap transition-all ${statusIdFilter === String(status.internal_code) ? 'bg-primary text-white shadow-md shadow-primary/20' : 'btn-ghost text-slate-500 hover:bg-slate-100'}`}
            >
              {status.name}
            </button>
          ))}
        </div>

        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="relative w-full md:w-1/2 lg:w-96">
            <input 
              type="text" 
              placeholder="جستجو در نام، موبایل، کد سفارش..." 
              className="input input-bordered w-full pl-10 bg-slate-50 focus:bg-white focus:border-primary transition-all rounded-xl"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          </div>

          <div className="flex w-full md:w-auto gap-2 items-center">
            <div className="relative">
              <input 
                type="date" 
                className="input input-bordered text-sm rounded-xl pl-10 bg-slate-50"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
              />
              <CalendarIcon className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            </div>
            
            {(searchQuery || statusIdFilter !== 'all' || dateFilter) && (
              <button onClick={resetFilters} className="btn btn-square btn-ghost text-error" title="حذف فیلترها">
                <FilterX size={18} />
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm min-h-[400px] relative">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-80 gap-4">
            <span className="loading loading-spinner loading-lg text-primary"></span>
            <span className="text-slate-400 font-medium animate-pulse">در حال بارگذاری اطلاعات...</span>
          </div>
        ) : (
          <div className="overflow-x-visible">
            <table className="table table-pin-rows w-full" style={{ borderCollapse: 'separate' }}>
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider relative z-10">
                <tr className="text-right">
                  <th className="w-12 bg-slate-50">
                    <input type="checkbox" className="checkbox checkbox-sm checkbox-primary rounded"
                      checked={orders.length > 0 && selectedIds.length === orders.length} onChange={handleToggleAll} />
                  </th>
                  <th className="bg-slate-50">شماره سفارش</th>
                  <th className="bg-slate-50">اطلاعات مشتری</th>
                  <th className="text-center bg-slate-50">وضعیت (کلیک برای تغییر)</th>
                  <th className="bg-slate-50">مبلغ کل</th>
                  <th className="text-center bg-slate-50">تعداد اقلام</th>
                  <th className="bg-slate-50">تاریخ ثبت</th>
                  <th className="text-center bg-slate-50">عملیات</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-right">
                {orders.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="text-center py-20 text-slate-400">
                      هیچ سفارشی با این فیلترها یافت نشد.
                    </td>
                  </tr>
                ) : (
                  orders.map((order) => {
                    const style = getStatusStyle(order.current_status_code);
                    return (
                      <tr key={order.id} className="hover:bg-slate-50/50 transition-colors group relative hover:z-20">
                        <th>
                          <input 
                            type="checkbox" 
                            className="checkbox checkbox-sm checkbox-primary rounded"
                            checked={selectedIds.includes(order.id)} 
                            onChange={() => handleToggleOne(order.id)} 
                          />
                        </th>
                        <td>
                          <div className="font-mono text-sm font-bold text-slate-700 bg-slate-100 inline-block px-2 py-1 rounded">
                            #{order.id}
                          </div>
                        </td>
                        <td>
                          <div className="flex flex-col">
                            <span className="font-bold text-slate-800">
                              {order.user_info?.full_name || order.recipient_name}
                            </span>
                            <span className="text-xs text-slate-400 mt-0.5">{order.recipient_phone}</span>
                          </div>
                        </td>
                        
                        <td className="text-center">
                          <div className="dropdown dropdown-bottom dropdown-end static sm:relative">
                            <div tabIndex={0} role="button" className="transition-transform active:scale-95 group-hover:ring-2 ring-primary/20 rounded-lg p-1 inline-block">
                              <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold ${style.badge}`}>
                                <div className={`w-1.5 h-1.5 rounded-full animate-pulse ${style.dot}`} />
                                {order.current_status}
                              </div>
                            </div>
                            <ul tabIndex={0} className="dropdown-content menu p-2 shadow-2xl bg-base-100 rounded-xl w-52 border border-slate-100 absolute z-[9999] mt-1">
                              <li className="menu-title text-[10px] text-slate-400">تغییر وضعیت به:</li>
                              {statuses?.map(s => (
                                <li key={s.id}>
                                  <button 
                                    type="button"
                                    onClick={() => openStatusModal(order, s.internal_code)}
                                    className={`w-full text-right px-4 py-2 text-sm rounded-lg block ${order.current_status_code === s.internal_code ? 'active bg-primary/10 text-primary font-bold' : 'hover:bg-slate-50'}`}
                                  >
                                    {s.name}
                                  </button>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </td>

                        <td>
                          <div className="font-black text-emerald-600 dir-ltr text-right text-base">
                            {formatPrice(order.total_price)}
                          </div>
                        </td>
                        <td className="text-center">
                          <div className="badge badge-ghost badge-sm border-slate-200">
                            {order.items?.length || 0} مورد
                          </div>
                        </td>
                        <td className="text-xs text-slate-500">
                          <div className="flex flex-col">
                            <span className="font-medium text-slate-700">{new Date(order.created_at).toLocaleDateString('EN')}</span>
                            <span className="text-slate-400 dir-ltr text-right">{new Date(order.created_at).toLocaleTimeString('EN', {hour: '2-digit', minute:'2-digit'})}</span>
                          </div>
                        </td>
                        <td>
                          <div className="flex items-center justify-center gap-1 opacity-100 lg:opacity-0 lg:group-hover:opacity-100 transition-opacity">
                             <button onClick={() => navigate(`/admin/orders/${order.id}`)} className="btn btn-square btn-ghost btn-sm text-primary hover:bg-primary/10" title="مشاهده جزئیات کامل">
                               <Eye size={18} />
                             </button>
                             <button onClick={() => {if(confirm('آیا از حذف مطمئن هستید؟')) deleteMutation.mutate(order.id)}} className="btn btn-square btn-ghost btn-sm text-error hover:bg-error/10" title="حذف سفارش">
                               <Trash2 size={18} />
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

        {!isLoading && orders.length > 0 && (
          <div className="p-4 border-t border-slate-100 bg-slate-50 flex flex-col md:flex-row items-center justify-between gap-4 relative z-10">
            <span className="text-sm text-slate-500 font-medium">
              نمایش صفحه <span className="font-bold text-slate-800">{currentPage}</span> از <span className="font-bold text-slate-800">{totalPages}</span>
            </span>
            <div className="join shadow-sm">
              <button className="join-item btn btn-sm bg-white border-slate-200 hover:bg-slate-100" disabled={currentPage === 1} onClick={() => setCurrentPage(p => p - 1)}>قبلی</button>
              <button className="join-item btn btn-sm bg-white border-slate-200 text-primary font-black pointer-events-none">{currentPage}</button>
              <button className="join-item btn btn-sm bg-white border-slate-200 hover:bg-slate-100" disabled={currentPage >= totalPages} onClick={() => setCurrentPage(p => p + 1)}>بعدی</button>
            </div>
          </div>
        )}
      </div>

      <BulkActionsBar 
        selectedCount={selectedIds.length}
        onClear={() => setSelectedIds([])}
        onDelete={handleBulkDelete}
      />

      {statusModalOpen && (
        <div className="fixed inset-0 z-[99999] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 animate-in fade-in">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
            <div className="p-6">
              <h3 className="text-lg font-black text-slate-800 mb-2">تایید تغییر وضعیت</h3>
              <p className="text-sm text-slate-500 mb-6">
                شما در حال تغییر وضعیت سفارش <span className="font-mono font-bold text-slate-800">#{selectedOrderForStatus?.id}</span> هستید.
              </p>

              <div className="flex gap-3 justify-end">
                <button 
                  type="button"
                  onClick={() => setStatusModalOpen(false)} 
                  className="btn btn-ghost"
                  disabled={changeStatusMutation.isPending}
                >
                  انصراف
                </button>
                <button 
                  type="button"
                  onClick={submitStatusChange} 
                  className="btn btn-primary px-8"
                  disabled={changeStatusMutation.isPending}
                >
                  {changeStatusMutation.isPending ? <span className="loading loading-spinner loading-sm"></span> : 'ثبت تغییرات'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default OrderListPage;