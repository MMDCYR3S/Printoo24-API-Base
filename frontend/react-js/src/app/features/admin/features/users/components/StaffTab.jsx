import { useState, useMemo } from 'react';
import { useAdminStaff } from '../hooks/useAdminStaff';
import { Plus, Shield, UserMinus, Trash2, Search } from 'lucide-react';
import StaffRow from './StaffRow';
import StaffModal from './StaffModal';

const StaffTab = () => {
  const { 
    staffQuery, 
    rolesQuery, 
    deleteMutation,
    bulkStatusMutation, 
    bulkDeleteMutation,
    bulkRoleMutation 
  } = useAdminStaff();

  const [selectedIds, setSelectedIds] = useState([]);
  const [roleFilter, setRoleFilter] = useState('all');
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingStaff, setEditingStaff] = useState(null);

  // Filters
  const filteredData = useMemo(() => {
    if (!staffQuery.data) return [];
    return staffQuery.data.filter(member => {
      if (roleFilter === 'all') return true;
      return member.role?.slug === roleFilter;
    });
  }, [staffQuery.data, roleFilter]);

  // Handlers
  const handleToggleAll = (e) => {
    if (e.target.checked) {
      setSelectedIds(filteredData.map(s => s.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleToggleOne = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const handleCreate = () => {
    setEditingStaff(null);
    setIsModalOpen(true);
  };

  const handleEdit = (staff) => {
    setEditingStaff(staff);
    setIsModalOpen(true);
  };

  const handleDelete = (id) => {
    if (window.confirm('آیا از حذف این کارمند اطمینان دارید؟')) {
      deleteMutation.mutate(id);
    }
  };

  // Bulk Handlers
  const handleBulkRole = (roleId) => {
    if (roleId && selectedIds.length > 0) {
      bulkRoleMutation.mutate({ user_ids: selectedIds, role_id: Number(roleId) }, {
        onSuccess: () => setSelectedIds([])
      });
    }
  };

  const handleBulkStatus = (isActive) => {
    bulkStatusMutation.mutate({ user_ids: selectedIds, is_active: isActive }, {
      onSuccess: () => setSelectedIds([])
    });
  };

  const handleBulkDelete = () => {
    if (window.confirm(`آیا از حذف ${selectedIds.length} کارمند اطمینان دارید؟`)) {
      bulkDeleteMutation.mutate(selectedIds, {
        onSuccess: () => setSelectedIds([])
      });
    }
  };

  if (staffQuery.isLoading) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center gap-4">
        <span className="loading loading-spinner loading-lg text-secondary"></span>
        <p className="text-slate-400 text-sm animate-pulse">در حال دریافت لیست کارمندان...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-32">
      {/* Header & Filters */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4 bg-white p-4 rounded-3xl border border-slate-100 shadow-sm">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Shield className="text-slate-400" size={20} />
          <select 
            className="select select-sm select-bordered w-full sm:w-48 bg-slate-50"
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
          >
            <option value="all">همه نقش‌ها</option>
            {rolesQuery.data?.map(role => (
              <option key={role.id} value={role.slug}>{role.name}</option>
            ))}
          </select>
        </div>
        
        <button onClick={handleCreate} className="btn btn-secondary btn-sm md:btn-md gap-2 shadow-lg shadow-secondary/20 rounded-xl w-full sm:w-auto">
          <Plus size={18} />
          تعریف کارمند جدید
        </button>
      </div>

      {/* Main Table */}
      <div className="bg-white rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/40 overflow-hidden relative min-h-[300px]">
        <div className="overflow-x-auto">
          <table className="table w-full">
            <thead className="bg-slate-50/80 text-slate-500 font-bold uppercase text-[11px] tracking-wider border-b border-slate-100">
              <tr className="text-right h-12">
                <th className="w-12">
                  <label className="cursor-pointer">
                    <input 
                      type="checkbox" 
                      className="checkbox checkbox-sm checkbox-secondary rounded-md" 
                      checked={filteredData.length > 0 && selectedIds.length === filteredData.length}
                      onChange={handleToggleAll} 
                    />
                  </label>
                </th>
                <th>کارمند</th>
                <th>نقش سازمانی</th>
                <th>وضعیت</th>
                <th>تاریخ ایجاد</th>
                <th className="text-left pl-6">عملیات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50 text-right bg-white">
              {filteredData.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-20">
                    <div className="flex flex-col items-center gap-4 opacity-40">
                      <div className="p-4 bg-slate-100 rounded-full">
                        <Search size={40} className="text-slate-400"/>
                      </div>
                      <p className="font-bold text-slate-500">کارمندی یافت نشد</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredData.map(member => (
                  <StaffRow 
                    key={member.id} 
                    member={member} 
                    isSelected={selectedIds.includes(member.id)}
                    onToggle={handleToggleOne}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                  />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bulk Actions Bar (Floating) */}
      {selectedIds.length > 0 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-slate-900 text-white px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-6 z-50 animate-in fade-in slide-in-from-bottom-4">
          <div className="flex items-center gap-3 border-l border-slate-700 pl-6">
            <span className="bg-secondary text-white w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shadow-lg shadow-secondary/30">
              {selectedIds.length}
            </span>
            <span className="text-sm font-medium">مورد انتخاب شده</span>
          </div>
          
          <div className="flex items-center gap-3">
            <select 
              className="select select-sm select-ghost bg-slate-800 text-xs border-slate-700 focus:bg-slate-700"
              onChange={(e) => handleBulkRole(e.target.value)}
              defaultValue=""
            >
              <option value="" disabled>تغییر نقش گروهی...</option>
              {rolesQuery.data?.map(role => (
                <option key={role.id} value={role.id}>{role.name}</option>
              ))}
            </select>

            <button onClick={() => handleBulkStatus(false)} className="btn btn-sm btn-ghost gap-2 text-warning hover:bg-warning/20">
              <UserMinus size={16} /> تعلیق
            </button>

            <button onClick={handleBulkDelete} className="btn btn-sm btn-ghost gap-2 text-error hover:bg-error/20">
              <Trash2 size={16} /> حذف
            </button>
          </div>
          
          <button onClick={() => setSelectedIds([])} className="btn btn-sm btn-circle btn-ghost hover:bg-slate-800">✕</button>
        </div>
      )}

      {/* Modal Render */}
      <StaffModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        initialData={editingStaff} 
      />
    </div>
  );
};

export default StaffTab;