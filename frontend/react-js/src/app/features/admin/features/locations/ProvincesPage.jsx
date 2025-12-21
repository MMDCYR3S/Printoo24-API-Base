import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Plus, Search, Map, Edit, X, Trash2 } from 'lucide-react';
import { useProvinces } from '../../hooks/useLocations';
import BulkActionsBar from '../users/components/BulkActionsBar'; // Import existing component

// Zod Schema
const provinceSchema = z.object({
  name: z.string().min(2, 'نام استان باید حداقل ۲ حرف باشد'),
});

const ProvincesPage = () => {
  const { provinces, isLoading, searchTerm, setSearchTerm, createMutation, updateMutation, bulkDeleteMutation } = useProvinces();
  
  // UI States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [selectedIds, setSelectedIds] = useState([]);

  // Form
  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm({
    resolver: zodResolver(provinceSchema)
  });

  // Handlers
  const openModal = (item = null) => {
    setEditingItem(item);
    if (item) setValue('name', item.name);
    else reset();
    setIsModalOpen(true);
  };

  const onSubmit = (data) => {
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.id, data }, { onSuccess: () => setIsModalOpen(false) });
    } else {
      createMutation.mutate(data, { onSuccess: () => setIsModalOpen(false) });
    }
  };

  // Selection Logic
  const toggleSelect = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };
  
  const toggleAll = () => {
    if (selectedIds.length === provinces.length) setSelectedIds([]);
    else setSelectedIds(provinces.map(p => p.id));
  };

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-black text-slate-800 flex items-center gap-2">
            <Map className="text-primary" /> مدیریت استان‌ها
          </h1>
          <p className="text-slate-500 text-sm mt-1">لیست استان‌های تحت پوشش ارسال</p>
        </div>
        <button onClick={() => openModal()} className="btn btn-primary gap-2 shadow-lg shadow-primary/20">
          <Plus size={20} /> افزودن استان
        </button>
      </div>

      {/* Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-3">
        <Search className="text-slate-400" size={20} />
        <input 
          type="text" 
          placeholder="جستجو نام استان..." 
          className="bg-transparent w-full outline-none text-slate-700 placeholder:text-slate-400"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
        <table className="table w-full">
          <thead className="bg-slate-50 text-slate-500 font-bold">
            <tr className='text-right'>
              <th className="w-12 text-right ">
                <input type="checkbox" className="checkbox checkbox-sm checkbox-primary" 
                  checked={provinces.length > 0 && selectedIds.length === provinces.length}
                  onChange={toggleAll}
                />
              </th>
              <th className='text-right'>نام استان</th>
              <th className='text-right'>نامک (Slug)</th>
              <th className="text-center w-24">عملیات</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
               <tr><td colSpan="4" className="text-center py-10"><span className="loading loading-spinner text-primary"></span></td></tr>
            ) : provinces.length === 0 ? (
               <tr><td colSpan="4" className="text-center py-10 text-slate-400">موردی یافت نشد.</td></tr>
            ) : (
              provinces.map((province) => (
                <tr key={province.id} className="hover:bg-slate-50 transition-colors">
                  <th>
                    <input type="checkbox" className="checkbox checkbox-sm checkbox-primary" 
                       checked={selectedIds.includes(province.id)}
                       onChange={() => toggleSelect(province.id)}
                    />
                  </th>
                  <td className="font-bold text-slate-700 text-lg text-right">{province.name}</td>
                  <td className="font-mono text-xs opacity-50 text-right">{province.slug}</td>
                  <td>
                    <button onClick={() => openModal(province)} className="btn btn-ghost btn-sm btn-square text-blue-500 hover:bg-blue-50">
                      <Edit size={16} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Bulk Actions (Reused) */}
      <BulkActionsBar 
        selectedCount={selectedIds.length}
        onClear={() => setSelectedIds([])}
        onDelete={() => {
            if(confirm('آیا از حذف مطمئن هستید؟')) {
                bulkDeleteMutation.mutate(selectedIds);
                setSelectedIds([]);
            }
        }}
        // دکمه‌های وضعیت رو برای استان‌ها غیرفعال می‌کنیم یا هندلر خالی میدیم
        onStatusChange={() => {}} 
      />

      {/* Modal */}
      <dialog className={`modal ${isModalOpen ? 'modal-open' : ''} backdrop-blur-sm`}>
        <div className="modal-box rounded-2xl">
          <button onClick={() => setIsModalOpen(false)} className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2"><X size={20}/></button>
          <h3 className="font-bold text-lg mb-4">{editingItem ? 'ویرایش استان' : 'افزودن استان جدید'}</h3>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="form-control">
              <label className="label text-sm font-bold text-slate-500">نام استان</label>
              <input type="text" {...register('name')} className="input input-bordered rounded-xl w-full" placeholder="مثال: تهران" />
              {errors.name && <span className="text-error text-xs mt-1">{errors.name.message}</span>}
            </div>
            <button type="submit" className="btn btn-primary w-full rounded-xl" disabled={createMutation.isPending || updateMutation.isPending}>
              {(createMutation.isPending || updateMutation.isPending) ? <span className="loading loading-spinner"></span> : 'ذخیره تغییرات'}
            </button>
          </form>
        </div>
      </dialog>
    </div>
  );
};

export default ProvincesPage;