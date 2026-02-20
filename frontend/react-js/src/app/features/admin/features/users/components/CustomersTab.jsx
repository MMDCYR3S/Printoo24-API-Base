import { useState, useMemo, useCallback } from 'react';
import { useCustomers } from '../hooks/useCustomers';
import { ChevronLeft, ChevronRight, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import CustomerModal from './CustomerModal';
import WalletAdjustModal from '../../../components/WalletAdjustModal';
import CustomerRow from './CustomerRow';
import CustomerFilters from './CustomerFilters';
import BulkActionsBar from './BulkActionsBar';

const ITEMS_PER_PAGE = 10;

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
  const [walletModalOpen, setWalletModalOpen] = useState(false);
  const [walletUser, setWalletUser] = useState(null);

  // منطق فیلتر و سورت (کپی از نسخه اصلی برای حفظ پایداری)
  const filteredUsers = useMemo(() => {
    if (!usersQuery.data) return [];
    
    return usersQuery.data.filter(user => {
      const matchesSearch = 
        user.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.last_name?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesStatus = statusFilter === 'all' || 
        (statusFilter === 'active' ? user.is_active : !user.is_active);
      
      const matchesRole = roleFilter === 'all' || 
        (roleFilter === 'staff' ? user.is_staff : !user.is_staff);

      return matchesSearch && matchesStatus && matchesRole;
    }).sort((a, b) => {
      if (!sortConfig.key) return 0;
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];
      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [usersQuery.data, searchTerm, statusFilter, roleFilter, sortConfig]);

  const totalPages = Math.ceil(filteredUsers.length / ITEMS_PER_PAGE);
  const currentData = filteredUsers.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  // Handlers
  const handleEdit = (user) => {
    setEditingUser(user);
    setIsModalOpen(true);
  };

  const handleWalletAdjust = (user) => {
    setWalletUser(user);
    setWalletModalOpen(true);
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedIds(currentData.map(u => u.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (id) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleBulkStatus = (status) => {
    bulkStatusMutation.mutate({ user_ids: selectedIds, is_active: status }, {
      onSuccess: () => setSelectedIds([])
    });
  };

  const handleBulkDelete = () => {
    if (window.confirm(`آیا از حذف ${selectedIds.length} کاربر اطمینان دارید؟`)) {
      bulkDeleteMutation.mutate(selectedIds, {
        onSuccess: () => setSelectedIds([])
      });
    }
  };

  if (usersQuery.isLoading) return <div className="p-10 text-center"><span className="loading loading-spinner text-primary"></span></div>;

  return (
    <div className="space-y-4">
      <CustomerFilters 
        searchTerm={searchTerm} setSearchTerm={setSearchTerm}
        statusFilter={statusFilter} setStatusFilter={setStatusFilter}
        roleFilter={roleFilter} setRoleFilter={setRoleFilter}
      />

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <table className="table table-zebra w-full">
          <thead>
            <tr className="bg-slate-50/50 border-b border-slate-100">
              <th className="w-12"><input type="checkbox" className="checkbox checkbox-sm" onChange={handleSelectAll} /></th>
              <th>کاربر</th>
              <th>وضعیت</th>
              <th>کیف پول</th>
              <th>تاریخ عضویت</th>
              <th className="text-left">عملیات</th>
            </tr>
          </thead>
          <tbody>
            {currentData.map(user => (
              <CustomerRow 
                key={user.id} 
                user={user} 
                isSelected={selectedIds.includes(user.id)}
                onSelect={() => handleSelectOne(user.id)}
                onEdit={() => handleEdit(user)}
                onWallet={() => handleWalletAdjust(user)}
              />
            ))}
          </tbody>
        </table>

        {/* Pagination */}
        {totalPages > 1 && (
            <div className="p-4 border-t border-slate-50 flex items-center justify-between bg-slate-50/30">
                <div className="join">
                    <button className="join-item btn btn-sm btn-ghost" disabled={currentPage === 1} onClick={() => setCurrentPage(p => p - 1)}>
                        <ChevronRight size={16}/>
                    </button>
                    <span className="join-item btn btn-sm btn-ghost pointer-events-none text-xs font-bold">
                        صفحه {currentPage} از {totalPages}
                    </span>
                    <button className="join-item btn btn-sm btn-ghost" disabled={currentPage === totalPages} onClick={() => setCurrentPage(p => p + 1)}>
                        <ChevronLeft size={16}/>
                    </button>
                </div>
            </div>
        )}
      </div>

      <BulkActionsBar 
        selectedCount={selectedIds.length}
        onClear={() => setSelectedIds([])}
        onStatusChange={handleBulkStatus}
        onDelete={handleBulkDelete}
      />

      {isModalOpen && (
          <CustomerModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} initialData={editingUser} />
      )}

      {walletModalOpen && (
         <WalletAdjustModal isOpen={walletModalOpen} onClose={() => setWalletModalOpen(false)} user={walletUser} />
      )}
    </div>
  );
};

export default CustomersTab;