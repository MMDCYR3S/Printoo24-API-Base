import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Plus, Search, MapPin, Edit, X } from 'lucide-react';
import { useCities, useProvinces } from '../../hooks/useLocations'; // Import both hooks
import BulkActionsBar from '../users/components/BulkActionsBar';

// Zod Schema
const citySchema = z.object({
  name: z.string().min(2, 'نام شهر الزامی است'),
  province: z.coerce.number().min(1, 'انتخاب استان الزامی است'),
});

const CitiesPage = () => {
  // Logic
  const { 
    cities, isLoading, 
    searchTerm, setSearchTerm, 
    selectedProvinceId, setSelectedProvinceId,
    createMutation, updateMutation, bulkDeleteMutation 
  } = useCities();

  // برای پر کردن سلکت باکس‌ها نیاز به لیست استان‌ها داریم
  const { allProvinces } = useProvinces(); 

  // UI States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [selectedIds, setSelectedIds] = useState([]);

  // Form
  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm({
    resolver: zodResolver(citySchema)
  });

  // Handlers
  const openModal = (item = null) => {
    setEditingItem(item);
    if (item) {
      setValue('name', item.name);
      setValue('province', item.province);
    } else {
      reset();
      // اگر فیلتر روی یک استان خاص بود، موقع ایجاد دیفالت همون رو انتخاب کن
      if(selectedProvinceId !== 'all') setValue('province', selectedProvinceId);
    }
    setIsModalOpen(true);
  };

  const onSubmit = (data) => {
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.id, data }, { onSuccess: () => setIsModalOpen(false) });
    } else {
      createMutation.mutate(data, { onSuccess: () => setIsModalOpen(false) });
    }
  };

  const toggleSelect = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };
  
  const toggleAll = () => {
    if (selectedIds.length === cities.length) setSelectedIds([]);
    else setSelectedIds(cities.map(c => c.id));
  };

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-800 flex items-center gap-2">
            <MapPin className="text-primary" /> مدیریت شهرها
          </h1>
          <p className="text-slate-500 text-sm mt-1">مدیریت لیست شهرها و ارتباط با استان</p>
        </div>
        <button onClick={() => openModal()} className="btn btn-primary gap-2 shadow-lg shadow-primary/20">
          <Plus size={20} /> افزودن شهر
        </button>
      </div>

      {/* Toolbar: Filter & Search */}
      <div className="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm flex flex-col md:flex-row gap-4">
        {/* Province Filter */}
        <div className="w-full md:w-64">
           <select 
             className="select select-bordered w-full focus:border-primary"
             value={selectedProvinceId}
             onChange={(e) => setSelectedProvinceId(e.target.value)}
           >
             <option value="all">همه استان‌ها</option>
             {allProvinces?.map(prov => (
               <option key={prov.id} value={prov.id}>{prov.name}</option>
             ))}
           </select>
        </div>

        {/* Search */}
        <div className="flex-1 relative">
           <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
           <input 
             type="text" 
             placeholder="جستجو نام شهر..." 
             className="input input-bordered w-full pr-10"
             value={searchTerm}
             onChange={e => setSearchTerm(e.target.value)}
           />
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden min-h-[400px]">
        <table className="table w-full">
          <thead className="bg-slate-50 text-slate-500 font-bold">
            <tr className='text-right'>
              <th className="w-12">
                <input type="checkbox" className="checkbox checkbox-sm checkbox-primary" 
                   checked={cities.length > 0 && selectedIds.length === cities.length}
                   onChange={toggleAll}
                />
              </th>
              <th>نام شهر</th>
              <th>استان</th>
              <th>Slug</th>
              <th className="text-center w-24">عملیات</th>
            </tr>
          </thead>
          <tbody className='text-right'>
            {isLoading ? (
               <tr><td colSpan="5" className="text-center py-10"><span className="loading loading-spinner text-primary"></span></td></tr>
            ) : cities.length === 0 ? (
               <tr><td colSpan="5" className="text-center py-10 text-slate-400">موردی یافت نشد.</td></tr>
            ) : (
              cities.map((city) => (
                <tr key={city.id} className="hover:bg-slate-50 transition-colors">
                  <th>
                    <input type="checkbox" className="checkbox checkbox-sm checkbox-primary" 
                       checked={selectedIds.includes(city.id)}
                       onChange={() => toggleSelect(city.id)}
                    />
                  </th>
                  <td className="font-bold text-slate-700">{city.name}</td>
                  <td>
                    <span className="badge badge-ghost font-medium">{city.province_name}</span>
                  </td>
                  <td className="font-mono text-xs opacity-50">{city.slug}</td>
                  <td>
                    <button onClick={() => openModal(city)} className="btn btn-ghost btn-sm btn-square text-blue-500 hover:bg-blue-50">
                      <Edit size={16} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Bulk Actions */}
      <BulkActionsBar 
        selectedCount={selectedIds.length}
        onClear={() => setSelectedIds([])}
        onDelete={() => {
            if(confirm('آیا از حذف شهرهای انتخاب شده مطمئن هستید؟')) {
                bulkDeleteMutation.mutate(selectedIds);
                setSelectedIds([]);
            }
        }}
        onStatusChange={() => {}} 
      />

      {/* Modal */}
      <dialog className={`modal ${isModalOpen ? 'modal-open' : ''} backdrop-blur-sm`}>
        <div className="modal-box rounded-2xl">
          <button onClick={() => setIsModalOpen(false)} className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2"><X size={20}/></button>
          <h3 className="font-bold text-lg mb-4">{editingItem ? 'ویرایش شهر' : 'افزودن شهر جدید'}</h3>
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Province Select in Form */}
            <div className="form-control">
              <label className="label text-sm font-bold text-slate-500">استان مربوطه</label>
              <select {...register('province')} className="select select-bordered w-full rounded-xl">
                <option value="">انتخاب کنید...</option>
                {allProvinces?.map(prov => (
                   <option key={prov.id} value={prov.id}>{prov.name}</option>
                ))}
              </select>
              {errors.province && <span className="text-error text-xs mt-1">{errors.province.message}</span>}
            </div>

            {/* City Name */}
            <div className="form-control">
              <label className="label text-sm font-bold text-slate-500">نام شهر</label>
              <input type="text" {...register('name')} className="input input-bordered rounded-xl w-full" placeholder="مثال: کرج" />
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

export default CitiesPage;