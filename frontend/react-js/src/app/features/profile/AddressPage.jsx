import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { MapPin, Plus, Trash2, X, Check } from 'lucide-react';
import { profileService } from '../../services/profileService';

const AddressPage = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const queryClient = useQueryClient();
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  // دریافت آدرس‌ها
  const { data: rawAddresses, isLoading } = useQuery({
    queryKey: ['addresses'],
    queryFn: profileService.getAddresses,
  });
  
  const addresses = Array.isArray(rawAddresses?.[0]) ? rawAddresses[0] : (rawAddresses || []);

  // افزودن آدرس
  const addMutation = useMutation({
    mutationFn: profileService.addAddress,
    onSuccess: () => {
      toast.success('آدرس جدید ثبت شد');
      queryClient.invalidateQueries(['addresses']);
      queryClient.invalidateQueries(['profile-addresses']); // برای آپدیت عدد داشبورد
      setIsModalOpen(false);
      reset();
    },
    onError: () => toast.error('خطا در ثبت آدرس')
  });

  // حذف آدرس
  const deleteMutation = useMutation({
    mutationFn: profileService.deleteAddress,
    onSuccess: () => {
      toast.success('آدرس حذف شد');
      queryClient.invalidateQueries(['addresses']);
      queryClient.invalidateQueries(['profile-addresses']);
    }
  });

  const onSubmit = (data) => {
    // تبدیل اعداد به فرمت API
    const payload = {
      ...data,
      province_id: Number(data.province_id),
      city_id: Number(data.city_id),
    };
    addMutation.mutate(payload);
  };

  if (isLoading) return <div className="text-center py-10"><span className="loading loading-spinner"></span></div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-black text-slate-800">آدرس‌های من</h1>
        <button onClick={() => setIsModalOpen(true)} className="btn btn-primary btn-sm gap-2 rounded-xl">
          <Plus size={18} /> آدرس جدید
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {addresses.map((addr) => (
          <div key={addr.id} className="bg-white p-5 rounded-3xl border border-slate-200 relative group">
            <div className="flex items-start gap-3 mb-3">
              <MapPin className="text-orange-500 mt-1" size={20} />
              <div>
                <span className="font-bold text-slate-800 block">{addr.province_detail?.name}، {addr.city_detail?.name}</span>
                <p className="text-sm text-slate-500 mt-1 leading-relaxed">{addr.address}</p>
              </div>
            </div>
            <div className="flex justify-between items-center pt-3 border-t border-slate-50">
              <span className="text-xs text-slate-400 bg-slate-50 px-2 py-1 rounded font-mono dir-ltr">
                Zip: {addr.postal_code}
              </span>
              <button 
                onClick={() => deleteMutation.mutate(addr.id)}
                className="btn btn-ghost btn-xs text-error hover:bg-error/10"
              >
                <Trash2 size={14} /> حذف
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* مودال افزودن آدرس */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-3xl w-full max-w-lg p-6 shadow-2xl animate-in fade-in zoom-in duration-200">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-bold text-lg">ثبت آدرس جدید</h3>
              <button onClick={() => setIsModalOpen(false)} className="btn btn-circle btn-sm btn-ghost"><X size={20}/></button>
            </div>
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="form-control">
                  <label className="label text-xs">ID استان</label>
                  <input type="number" placeholder="مثلا 1" className="input input-bordered rounded-xl" {...register('province_id', {required: true})} />
                </div>
                <div className="form-control">
                  <label className="label text-xs">ID شهر</label>
                  <input type="number" placeholder="مثلا 12" className="input input-bordered rounded-xl" {...register('city_id', {required: true})} />
                </div>
              </div>
              <div className="form-control">
                <label className="label text-xs">کد پستی (۱۰ رقم)</label>
                <input type="text" maxLength={10} className="input input-bordered rounded-xl text-left dir-ltr" {...register('postal_code', {required: true, minLength: 10})} />
              </div>
              <div className="form-control">
                <label className="label text-xs">آدرس دقیق</label>
                <textarea className="textarea textarea-bordered rounded-xl h-24" {...register('address', {required: true})}></textarea>
              </div>
              
              <button type="submit" className="btn btn-primary w-full rounded-xl mt-4" disabled={addMutation.isPending}>
                {addMutation.isPending ? <span className="loading loading-spinner"></span> : 'ثبت آدرس'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AddressPage;