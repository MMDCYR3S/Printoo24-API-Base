import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { Plus, Edit, Trash2, Layers, X } from 'lucide-react';
import { adminMasterDataService } from '../../services/adminMasterDataService';

// 1. اسکیما ولیدیشن
const quantitySchema = z.object({
  value: z.coerce.number().min(1, 'مقدار تیراژ باید حداقل ۱ باشد'),
});

const ProductQuantitiesPage = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm({
    resolver: zodResolver(quantitySchema),
  });

  // دریافت لیست
  const { data: quantities, isLoading } = useQuery({
    queryKey: ['admin-quantities'],
    queryFn: adminMasterDataService.getQuantities,
  });

  // Mutation: افزودن/ویرایش
  const saveMutation = useMutation({
    mutationFn: (data) => {
      if (editingItem) {
        return adminMasterDataService.updateQuantity({ id: editingItem.id, data });
      }
      return adminMasterDataService.addQuantity(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-quantities']);
      toast.success(editingItem ? 'تیراژ ویرایش شد' : 'تیراژ جدید اضافه شد');
      closeModal();
    },
    onError: () => toast.error('خطا در ذخیره سازی'),
  });

  // Mutation: حذف
  const deleteMutation = useMutation({
    mutationFn: adminMasterDataService.deleteQuantity,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-quantities']);
      toast.success('تیراژ حذف شد');
    },
  });

  const openModal = (item = null) => {
    setEditingItem(item);
    if (item) {
      setValue('value', item.value);
    } else {
      reset();
    }
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingItem(null);
    reset();
  };

  const handleDelete = (id) => {
    if (window.confirm('آیا از حذف این تیراژ اطمینان دارید؟')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div className="p-10 text-center"><span className="loading loading-spinner text-primary"></span></div>;

  return (
    <div className="space-y-6">
      {/* هدر صفحه */}
      <div className="flex justify-between items-center bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-purple-50 text-purple-600 rounded-xl">
            <Layers size={24} />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-800">مدیریت تیراژها</h1>
            <p className="text-xs text-slate-500">تعدادهای قابل سفارش (۱۰۰۰، ۲۰۰۰، ...)</p>
          </div>
        </div>
        <button onClick={() => openModal()} className="btn btn-primary gap-2 rounded-xl shadow-lg shadow-primary/20">
          <Plus size={18} /> افزودن تیراژ
        </button>
      </div>

      {/* جدول داده‌ها */}
      <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden max-w-2xl mx-auto md:max-w-full">
        <table className="table w-full">
          <thead className="bg-slate-50 text-slate-500 font-bold">
            <tr>
              <th className="w-16">#</th>
              <th>مقدار تیراژ</th>
              <th className="text-center w-32">عملیات</th>
            </tr>
          </thead>
          <tbody>
            {quantities?.map((item, index) => (
              <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                <th>{index + 1}</th>
                <td className="font-bold text-lg text-slate-700 dir-ltr text-left">
                  {new Intl.NumberFormat('en-US').format(item.value)} <span className="text-xs text-slate-400 font-normal">عدد</span>
                </td>
                <td>
                  <div className="flex justify-center gap-2">
                    <button onClick={() => openModal(item)} className="btn btn-square btn-ghost btn-sm text-blue-600 hover:bg-blue-50">
                      <Edit size={16} />
                    </button>
                    <button onClick={() => handleDelete(item.id)} className="btn btn-square btn-ghost btn-sm text-red-500 hover:bg-red-50">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {quantities?.length === 0 && (
              <tr>
                <td colSpan="3" className="text-center py-10 text-slate-400">هیچ تیراژی تعریف نشده است.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* مودال فرم */}
      <dialog className={`modal ${isModalOpen ? 'modal-open' : ''} backdrop-blur-sm`}>
        <div className="modal-box rounded-3xl max-w-sm">
          <button onClick={closeModal} className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">
             <X size={20} />
          </button>
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            {editingItem ? <Edit size={18} className="text-primary"/> : <Plus size={18} className="text-primary"/>}
            {editingItem ? 'ویرایش تیراژ' : 'افزودن تیراژ جدید'}
          </h3>
          
          <form onSubmit={handleSubmit((data) => saveMutation.mutate(data))} className="space-y-4">
            <div className="form-control">
              <label className="label text-xs font-bold text-slate-500">مقدار (تعداد)</label>
              <input 
                type="number" 
                placeholder="مثلاً 1000" 
                className="input input-bordered rounded-xl text-center dir-ltr text-lg font-bold" 
                {...register('value')} 
              />
              {errors.value && <span className="text-error text-xs mt-1">{errors.value.message}</span>}
            </div>

            <button type="submit" className="btn btn-primary w-full rounded-xl mt-2" disabled={saveMutation.isPending}>
              {saveMutation.isPending ? <span className="loading loading-spinner"></span> : 'ذخیره تغییرات'}
            </button>
          </form>
        </div>
        <form method="dialog" className="modal-backdrop">
           <button onClick={closeModal}>close</button>
        </form>
      </dialog>
    </div>
  );
};

export default ProductQuantitiesPage;