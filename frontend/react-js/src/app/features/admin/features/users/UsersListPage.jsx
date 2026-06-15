import { useState, useMemo, useCallback } from 'react';
import { useCustomers } from '../../hooks/useCustomers';
import { Plus, ChevronLeft, ChevronRight, ArrowUpDown, ArrowUp, ArrowDown, Search, Users, ShieldCheck } from 'lucide-react';
import CustomerModal from './components/CustomerModal';
import WalletAdjustModal from '../../components/WalletAdjustModal'; 
import CustomerRow from './components/CustomerRow';
import CustomerFilters from './components/CustomerFilters';
import BulkActionsBar from './components/BulkActionsBar';

// کامپوننت تب کارمندان (که در فایل مجزا میسازیم)
import StaffTab from './components/StaffTab';

const ITEMS_PER_PAGE = 10;

// ==========================================
// 1. کدهای اورجینال شما بدون هیچ تغییری (فقط اسمش شد CustomersTab)
// ==========================================
const CustomersTab = () => {
  const { usersQuery, bulkStatusMutation, bulkDeleteMutation } = useCustomers();
  
  // Data States
  const [selectedIds, setSelectedIds] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [roleFilter, setRoleFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });
  
  // Modal States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  // Wallet Modal States
  const [walletModalOpen, setWalletModalOpen] = useState(false);
  const [walletUser, setWalletUser] = useState(null);

  // --- Filtering & Sorting Logic ---
  const processedData = useMemo(() => {
    if (!usersQuery.data) return [];
    
    let result = usersQuery.data.filter(user => {
      // Search Logic
      const term = searchTerm.toLowerCase();
      const matchesSearch = 
      (user.phone_number?.includes(term)) ||
      (user.first_name?.toLowerCase().includes(term)) ||
      (user.last_name?.toLowerCase().includes(term));
      
      // Status Logic
      const matchesStatus = statusFilter === 'all' 
        ? true 
        : statusFilter === 'active' ? user.is_active : !user.is_active;

      // Role Logic
      const matchesRole = roleFilter === 'all'
        ? true
        : roleFilter === 'admin' ? user.is_staff : !user.is_staff;

      return matchesSearch && matchesStatus && matchesRole;
    });

    // Sorting Logic
    result.sort((a, b) => {
      let aValue = a[sortConfig.key];
      let bValue = b[sortConfig.key];

      if (!aValue) aValue = '';
      if (!bValue) bValue = '';

      // Numeric check for wallet
      if (sortConfig.key === 'wallet_balance') {
         aValue = parseFloat(aValue) || 0;
         bValue = parseFloat(bValue) || 0;
      }

      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [usersQuery.data, searchTerm, statusFilter, roleFilter, sortConfig]);

  // --- Pagination Logic ---
  const totalPages = Math.ceil(processedData.length / ITEMS_PER_PAGE);
  const paginatedData = processedData.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  // --- Action Handlers ---
  const handleToggleOne = useCallback((id) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  }, []);

  const handleToggleAll = () => {
    if (selectedIds.length === paginatedData.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(paginatedData.map(u => u.id));
    }
  };

  const handleSort = (key) => {
    setSortConfig(current => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  // Edit Handler
  const handleEdit = useCallback((user) => {
    setEditingUser(user);
    setIsModalOpen(true);
  }, []);

  // Wallet Handler
  const handleWalletAction = useCallback((user) => {
    setWalletUser(user);
    setWalletModalOpen(true);
  }, []);

  // Create Handler
  const handleCreate = () => {
    setEditingUser(null);
    setIsModalOpen(true);
  };

  // Bulk Handlers
  const handleBulkDelete = () => {
    if (window.confirm(`آیا مطمئن هستید که می‌خواهید ${selectedIds.length} کاربر را حذف کنید؟`)) {
      bulkDeleteMutation.mutate(selectedIds);
      setSelectedIds([]);
    }
  };

  const handleBulkStatus = (active) => {
    bulkStatusMutation.mutate({ ids: selectedIds, active });
    setSelectedIds([]);
  };

  // Helper for Sort Icons
  const SortIcon = ({ columnKey }) => {
    if (sortConfig.key !== columnKey) return <ArrowUpDown size={14} className="opacity-20" />;
    return sortConfig.direction === 'asc' ? <ArrowUp size={14} className="text-primary" /> : <ArrowDown size={14} className="text-primary" />;
  };

  // Loading State
  if (usersQuery.isLoading) {
    return (
        <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4">
            <span className="loading loading-spinner loading-lg text-primary"></span>
            <p className="text-slate-400 text-sm animate-pulse">در حال دریافت لیست کاربران...</p>
        </div>
    );
  }

  return (
    <div className="p-6 md:p-8 max-w-[1920px] mx-auto space-y-8 pb-32"> 
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-6 border-b border-slate-200/60 pb-6">
        <div>
          <h1 className="text-3xl font-black text-slate-800 tracking-tight">مدیریت کاربران</h1>
          <p className="text-slate-500 text-sm mt-2 font-medium">
            لیست تمام کاربران، کارمندان و وضعیت حساب‌ها
          </p>
        </div>
        <div className="flex items-center gap-3">
            <div className="bg-slate-100 text-slate-500 px-4 py-2 rounded-xl text-xs font-bold border border-slate-200">
                مجموع: {usersQuery.data?.length || 0}
            </div>
            <button onClick={handleCreate} className="btn btn-primary gap-2 shadow-lg shadow-primary/20 px-6 rounded-xl hover:scale-105 transition-transform">
            <Plus size={20} />
            کاربر جدید
            </button>
        </div>
      </div>

      {/* Filters Section */}
        <CustomerFilters 
            searchTerm={searchTerm}
            onSearchChange={setSearchTerm}
            statusFilter={statusFilter}
            onStatusChange={setStatusFilter}
            roleFilter={roleFilter}
            onRoleChange={setRoleFilter}
            onRefresh={() => usersQuery.refetch()}
        />

      {/* Main Table */}
      <div className="bg-white rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/40 overflow-hidden relative  ">
        <div className="">
          <table className="table w-full">
            {/* Table Head */}
            <thead className="bg-slate-50/80 text-slate-500 font-bold uppercase text-[11px] tracking-wider border-b border-slate-100 backdrop-blur-sm sticky top-0 z-10">
              <tr className='text-right h-12'>
                <th className="w-12">
                  <label className="cursor-pointer">
                    <input 
                      type="checkbox" 
                      className="checkbox checkbox-sm checkbox-primary rounded-md"
                      checked={paginatedData.length > 0 && selectedIds.length === paginatedData.length}
                      onChange={handleToggleAll}
                    />
                  </label>
                </th>
                
                <th onClick={() => handleSort('phone_number')} className="cursor-pointer hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-2">کاربر <SortIcon columnKey="username"/></div>
                </th>
                
                <th onClick={() => handleSort('is_active')} className="cursor-pointer hover:bg-slate-100 transition-colors w-28">
                  <div className="flex items-center gap-2">وضعیت <SortIcon columnKey="is_active"/></div>
                </th>
                
                <th onClick={() => handleSort('is_staff')} className="cursor-pointer hover:bg-slate-100 transition-colors w-28">
                   <div className="flex items-center gap-2">نقش <SortIcon columnKey="is_staff"/></div>
                </th>
                
                <th onClick={() => handleSort('wallet_balance')} className="cursor-pointer hover:bg-slate-100 transition-colors text-right w-40">
                   <div className="flex items-center justify-end gap-2">موجودی <SortIcon columnKey="wallet_balance"/></div>
                </th>
                
                <th onClick={() => handleSort('created_at')} className="cursor-pointer hover:bg-slate-100 transition-colors w-40">
                   <div className="flex items-center gap-2">تاریخ عضویت <SortIcon columnKey="created_at"/></div>
                </th>
                
                <th className="text-left w-24 pl-6">عملیات</th>
              </tr>
            </thead>
            
            {/* Table Body */}
            <tbody className="divide-y divide-slate-50 text-right bg-white">
              {paginatedData.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-32">
                    <div className="flex flex-col items-center gap-4 opacity-40">
                        <div className="p-4 bg-slate-100 rounded-full">
                            <Search size={40} className="text-slate-400"/>
                        </div>
                        <p className="font-bold text-slate-500">کاربری یافت نشد</p>
                    </div>
                  </td>
                </tr>
              ) : (
                paginatedData.map((user) => (
                  
                  <CustomerRow
                    key={user.id} 
                    user={user} 
                    isSelected={selectedIds.includes(user.id)}
                    onToggle={handleToggleOne}
                    onEdit={handleEdit}
                    onWalletAction={handleWalletAction} 
                  />
                  
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        {totalPages > 1 && (
            <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-center lg:justify-end">
                <div className="join bg-white shadow-sm border border-slate-200 rounded-xl overflow-hidden">
                    <button 
                        className="join-item btn btn-sm btn-ghost border-l border-slate-200 rounded-none disabled:bg-transparent px-4 hover:bg-slate-50" 
                        disabled={currentPage === 1}
                        onClick={() => setCurrentPage(p => p - 1)}
                    >
                        <ChevronRight size={16}/>
                    </button>
                    <span className="join-item btn btn-sm btn-ghost pointer-events-none font-mono text-slate-600 px-4 text-xs font-bold">
                        Page {currentPage} of {totalPages}
                    </span>
                    <button 
                        className="join-item btn btn-sm btn-ghost border-r border-slate-200 rounded-none disabled:bg-transparent px-4 hover:bg-slate-50" 
                        disabled={currentPage === totalPages}
                        onClick={() => setCurrentPage(p => p + 1)}
                    >
                        <ChevronLeft size={16}/>
                    </button>
                </div>
            </div>
        )}
      </div>

      {/* Floating Bulk Actions */}
      <BulkActionsBar 
        selectedCount={selectedIds.length}
        onClear={() => setSelectedIds([])}
        onStatusChange={handleBulkStatus}
        onDelete={handleBulkDelete}
      />

      {/* Modals */}
      {isModalOpen && (
          <CustomerModal 
            isOpen={isModalOpen} 
            onClose={() => setIsModalOpen(false)} 
            initialData={editingUser}
          />
      )}

      {walletModalOpen && (
         <WalletAdjustModal 
           isOpen={walletModalOpen}
           onClose={() => setWalletModalOpen(false)}
           user={walletUser}
         />
      )}

    </div>
  );
};


// ==========================================
// 2. کامپوننت پوشه‌بندی و تب‌ها (حالا به درستی دور کدهای شما قرار گرفت)
// ==========================================
const UsersListPage = () => {
  const [activeTab, setActiveTab] = useState('customers'); // 'customers' or 'staff'

  return (
    <div className="w-full relative">
      {/* هدر تب‌ها در بالاترین سطح صفحه قرار می‌گیرد */}
      <div className="pt-6 px-6 md:px-8 max-w-[1920px] mx-auto">
        {/* <div className="tabs tabs-boxed bg-slate-100 p-1 w-fit border border-slate-200 shadow-sm rounded-xl">
          <button 
            onClick={() => setActiveTab('customers')}
            className={`tab tab-md md:tab-lg gap-2 transition-all rounded-lg ${activeTab === 'customers' ? 'tab-active !bg-white !text-primary shadow-sm font-bold' : 'text-slate-500 font-medium'}`}
          >
            <Users size={18} />
            کاربران
          </button>
          <button 
            onClick={() => setActiveTab('staff')}
            className={`tab tab-md md:tab-lg gap-2 transition-all rounded-lg ${activeTab === 'staff' ? 'tab-active !bg-white !text-secondary shadow-sm font-bold' : 'text-slate-500 font-medium'}`}
          >
            <ShieldCheck size={18} />
            کارمندان
          </button>
        </div> */}
      </div>

      {/* محتوای تب انتخاب شده */}
      <div className="transition-all duration-300">
        {activeTab === 'customers' ? <CustomersTab /> : <StaffTab />}
      </div>
    </div>
  );
};

export default UsersListPage;