import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { Plus, Edit, Trash2, Ruler, X } from 'lucide-react';
import { adminMasterDataService } from '../../services/adminMasterDataService';

// 1. اسکیما ولیدیشن (اعداد باید نامبر باشن)
const sizeSchema = z.object({
  name: z.string().min(1, 'نام سایز الزامی است'),
  width: z.coerce.number().min(1, 'عرض باید بیشتر از ۰ باشد'),
  height: z.coerce.number().min(1, 'ارتفاع باید بیشتر از ۰ باشد'),
});

const ProductSizesPage = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  // فرم
  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm({
    resolver: zodResolver(sizeSchema),
  });

  // دریافت لیست
  const { data: sizes, isLoading } = useQuery({
    queryKey: ['admin-sizes'],
    queryFn: adminMasterDataService.getSizes,
  });

  // Mutation: افزودن/ویرایش
  const saveMutation = useMutation({
    mutationFn: (data) => {
      if (editingItem) {
        return adminMasterDataService.updateSize({ id: editingItem.id, data });
      }
      return adminMasterDataService.addSize(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-sizes']);
      toast.success(editingItem ? 'سایز ویرایش شد' : 'سایز جدید اضافه شد');
      closeModal();
    },
    onError: () => toast.error('خطا در ذخیره سازی'),
  });

  // Mutation: حذف
  const deleteMutation = useMutation({
    mutationFn: adminMasterDataService.deleteSize,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-sizes']);
      toast.success('سایز حذف شد');
    },
  });

  // هندلرها
  const openModal = (item = null) => {
    setEditingItem(item);
    if (item) {
      setValue('name', item.name);
      setValue('width', item.width);
      setValue('height', item.height);
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
    if (window.confirm('آیا از حذف این سایز اطمینان دارید؟')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div className="p-10 text-center"><span className="loading loading-spinner text-primary"></span></div>;

  return (
    <div className="space-y-6">
      {/* هدر صفحه */}
      <div className="flex justify-between items-center bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
            <Ruler size={24} />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-800">مدیریت سایزها</h1>
            <p className="text-xs text-slate-500">ابعاد استاندارد چاپ (A4, A5, ...)</p>
          </div>
        </div>
        <button onClick={() => openModal()} className="btn btn-primary gap-2 rounded-xl shadow-lg shadow-primary/20">
          <Plus size={18} /> افزودن سایز
        </button>
      </div>

      {/* جدول داده‌ها */}
      <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="table w-full">
            <thead className="bg-slate-50 text-slate-500 font-bold">
              <tr>
                <th>#</th>
                <th>نام سایز</th>
                <th className="text-center">ابعاد (cm)</th>
                <th className="text-center">عملیات</th>
              </tr>
            </thead>
            <tbody>
              {sizes?.map((item, index) => (
                <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                  <th>{index + 1}</th>
                  <td className="font-bold text-slate-700">{item.name}</td>
                  <td className="text-center dir-ltr">
                    <span className="badge badge-ghost font-mono">{item.width} x {item.height}</span>
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
              {sizes?.length === 0 && (
                <tr>
                  <td colSpan="4" className="text-center py-10 text-slate-400">هیچ سایزی تعریف نشده است.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* مودال فرم (DaisyUI Modal) */}
      <dialog className={`modal ${isModalOpen ? 'modal-open' : ''} backdrop-blur-sm`}>
        <div className="modal-box rounded-3xl max-w-sm">
          <button onClick={closeModal} className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">
             <X size={20} />
          </button>
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            {editingItem ? <Edit size={18} className="text-primary"/> : <Plus size={18} className="text-primary"/>}
            {editingItem ? 'ویرایش سایز' : 'افزودن سایز جدید'}
          </h3>
          
          <form onSubmit={handleSubmit((data) => saveMutation.mutate(data))} className="space-y-4">
            <div className="form-control">
              <label className="label text-xs font-bold text-slate-500">نام سایز (مثال: A4)</label>
              <input type="text" className="input input-bordered rounded-xl" {...register('name')} />
              {errors.name && <span className="text-error text-xs mt-1">{errors.name.message}</span>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="form-control">
                <label className="label text-xs font-bold text-slate-500">عرض (cm)</label>
                <input type="number" step="0.1" className="input input-bordered rounded-xl text-center dir-ltr" {...register('width')} />
                {errors.width && <span className="text-error text-xs mt-1">{errors.width.message}</span>}
              </div>
              <div className="form-control">
                <label className="label text-xs font-bold text-slate-500">ارتفاع (cm)</label>
                <input type="number" step="0.1" className="input input-bordered rounded-xl text-center dir-ltr" {...register('height')} />
                {errors.height && <span className="text-error text-xs mt-1">{errors.height.message}</span>}
              </div>
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

export default ProductSizesPage;