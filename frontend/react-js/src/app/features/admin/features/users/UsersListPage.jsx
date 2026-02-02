// src/app/features/admin/customers/components/CustomerList.jsx
import { useState, useMemo, useCallback } from 'react';
import { useCustomers } from '../../hooks/useCustomers';
import { Plus, ChevronLeft, ChevronRight, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import CustomerModal from './components/CustomerModal';
import CustomerRow from './components/CustomerRow';
import CustomerFilters from './components/CustomerFilters';
import BulkActionsBar from './components/BulkActionsBar';

const ITEMS_PER_PAGE = 10;

const CustomerList = () => {
  const { usersQuery, bulkStatusMutation, bulkDeleteMutation } = useCustomers();
  
  // States
  const [selectedIds, setSelectedIds] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [roleFilter, setRoleFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' }); // Sorting State
  
  // Modal States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  // --- Filtering & Sorting Logic ---
  const processedData = useMemo(() => {
    if (!usersQuery.data) return [];
    
    let result = usersQuery.data.filter(user => {
      // Search
      const term = searchTerm.toLowerCase();
      const matchesSearch = 
        (user.username?.toLowerCase().includes(term)) ||
        (user.email?.toLowerCase().includes(term)) ||
        (user.phone_number?.includes(term)) ||
        (user.first_name?.toLowerCase().includes(term)) ||
        (user.last_name?.toLowerCase().includes(term));
      
      // Status Filter
      const matchesStatus = statusFilter === 'all' 
        ? true 
        : statusFilter === 'active' ? user.is_active : !user.is_active;

      // Role Filter
      const matchesRole = roleFilter === 'all'
        ? true
        : roleFilter === 'admin' ? user.is_staff : !user.is_staff;

      return matchesSearch && matchesStatus && matchesRole;
    });

    // Sorting
    result.sort((a, b) => {
      let aValue = a[sortConfig.key];
      let bValue = b[sortConfig.key];

      // Handle nulls
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

  // --- Pagination ---
  const totalPages = Math.ceil(processedData.length / ITEMS_PER_PAGE);
  const paginatedData = processedData.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  // --- Handlers ---
  // استفاده از useCallback برای جلوگیری از رندر مجدد Rowها
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

  const handleEdit = useCallback((user) => {
    setEditingUser(user);
    setIsModalOpen(true);
  }, []);

  const handleCreate = () => {
    setEditingUser(null);
    setIsModalOpen(true);
  };

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

  if (usersQuery.isLoading) return <div className="p-12 text-center loading loading-spinner text-primary"></div>;

  // Helper for Sort Icons
  const SortIcon = ({ columnKey }) => {
    if (sortConfig.key !== columnKey) return <ArrowUpDown size={14} className="opacity-30" />;
    return sortConfig.direction === 'asc' ? <ArrowUp size={14} className="text-primary" /> : <ArrowDown size={14} className="text-primary" />;
  };

  return (
    <div className="p-6 max-w-[1800px] mx-auto space-y-6 pb-24"> {/* pb-24 for floating bar space */}
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-800">مدیریت کاربران</h1>
          <p className="text-slate-500 text-sm mt-1">
            <span className="font-bold text-slate-800">{usersQuery.data?.length || 0}</span> کاربر ثبت شده
          </p>
        </div>
        <button onClick={handleCreate} className="btn btn-primary gap-2 shadow-lg shadow-primary/20 px-6">
          <Plus size={20} />
          کاربر جدید
        </button>
      </div>

      {/* Filters Component */}
      <CustomerFilters 
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        statusFilter={statusFilter}
        onStatusChange={setStatusFilter}
        roleFilter={roleFilter}
        onRoleChange={setRoleFilter}
        onRefresh={() => usersQuery.refetch()}
      />

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="table w-full">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase text-xs tracking-wider">
              <tr className='text-right'>
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
                
                <th onClick={() => handleSort('username')} className="cursor-pointer hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-2">کاربر <SortIcon columnKey="username"/></div>
                </th>
                
                <th onClick={() => handleSort('is_active')} className="cursor-pointer hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-2">وضعیت <SortIcon columnKey="is_active"/></div>
                </th>
                
                <th onClick={() => handleSort('is_staff')} className="cursor-pointer hover:bg-slate-100 transition-colors">
                   <div className="flex items-center gap-2">نقش <SortIcon columnKey="is_staff"/></div>
                </th>
                
                <th onClick={() => handleSort('wallet_balance')} className="cursor-pointer hover:bg-slate-100 transition-colors">
                   <div className="flex items-center gap-2">کیف پول <SortIcon columnKey="wallet_balance"/></div>
                </th>
                
                <th onClick={() => handleSort('created_at')} className="cursor-pointer hover:bg-slate-100 transition-colors">
                   <div className="flex items-center gap-2">تاریخ عضویت <SortIcon columnKey="created_at"/></div>
                </th>
                
                <th className="text-left w-20">عملیات</th>
              </tr>
            </thead>
            
            <tbody className="divide-y divide-slate-100 text-right">
              {paginatedData.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-20">
                    <div className="flex flex-col items-center gap-2 opacity-50">
                        <span className="text-4xl">🔍</span>
                        <p>هیچ کاربری با این مشخصات یافت نشد</p>
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
                  />
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex justify-center lg:justify-end">
            <div className="join bg-white shadow-sm border border-slate-200 rounded-lg overflow-hidden">
                <button 
                    className="join-item btn btn-sm btn-ghost border-l border-slate-200 rounded-none disabled:bg-transparent" 
                    disabled={currentPage === 1}
                    onClick={() => setCurrentPage(p => p - 1)}
                >
                    <ChevronRight size={16}/>
                </button>
                <span className="join-item btn btn-sm btn-ghost pointer-events-none font-mono text-slate-600">
                     Page {currentPage} of {totalPages || 1}
                </span>
                <button 
                    className="join-item btn btn-sm btn-ghost border-r border-slate-200 rounded-none disabled:bg-transparent" 
                    disabled={currentPage === totalPages}
                    onClick={() => setCurrentPage(p => p + 1)}
                >
                    <ChevronLeft size={16}/>
                </button>
            </div>
        </div>
      </div>

      {/* Floating Bulk Actions */}
      <BulkActionsBar 
        selectedCount={selectedIds.length}
        onClear={() => setSelectedIds([])}
        onStatusChange={handleBulkStatus}
        onDelete={handleBulkDelete}
      />

      {/* Modal */}
      {isModalOpen && (
          <CustomerModal 
            isOpen={isModalOpen} 
            onClose={() => setIsModalOpen(false)} 
            initialData={editingUser}
          />
      )}

    </div>
  );
};

export default CustomerList;