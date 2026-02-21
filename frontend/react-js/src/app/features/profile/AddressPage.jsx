import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { MapPin, Plus, Trash2, X, AlertCircle } from 'lucide-react';
import { profileService } from '../../services/profileService';

import pageText from '../../lang/pages.json';
import globalText from '../../lang/global.json';

const AddressPage = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const queryClient = useQueryClient();
  
  const { 
    register, 
    handleSubmit, 
    reset, 
    watch, 
    setValue, 
    formState: { errors } 
  } = useForm();

  // رصد لحظه‌ای استان انتخاب شده برای لود شهرها
  const selectedProvinceId = watch('province_id');

  // --- دریافت داده‌ها ---

  // 1. لیست آدرس‌های فعلی
  const { data: rawAddresses, isLoading: isAddressesLoading } = useQuery({
    queryKey: ['addresses'],
    queryFn: profileService.getAddresses,
  });
  const addresses = Array.isArray(rawAddresses?.[0]) ? rawAddresses[0] : (rawAddresses || []);

  // 2. لیست استان‌ها (فقط یکبار لود شود)
  const { data: provinces, isLoading: isProvincesLoading } = useQuery({
    queryKey: ['provinces'],
    queryFn: profileService.getProvinces,
    staleTime: Infinity, // استان‌ها به ندرت تغییر می‌کنند
  });

  // 3. لیست شهرها (وابسته به استان انتخاب شده)
  const { data: cities, isLoading: isCitiesLoading } = useQuery({
    queryKey: ['cities', selectedProvinceId],
    queryFn: () => profileService.getCities(selectedProvinceId),
    enabled: !!selectedProvinceId, // تا استانی انتخاب نشود، درخواست نزن
  });

  // وقتی استان عوض شد، شهر قبلی را پاک کن
  useEffect(() => {
    setValue('city_id', '');
  }, [selectedProvinceId, setValue]);


  // --- عملیات (Mutations) ---

  const addMutation = useMutation({
    mutationFn: profileService.addAddress,
    onSuccess: () => {
      toast.success(pageText.profile.addressPage.registeredAddressSuccess);
      queryClient.invalidateQueries(['addresses']);
      queryClient.invalidateQueries(['profile-addresses']);
      setIsModalOpen(false);
      reset();
    },
    onError: (err) => {
      const msg = err?.response?.data?.detail || pageText.profile.addressPage.checkInputsError;
      toast.error(msg);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: profileService.deleteAddress,
    onSuccess: () => {
      toast.success('آدرس حذف شد');
      queryClient.invalidateQueries(['addresses']);
      queryClient.invalidateQueries(['profile-addresses']);
    },
    onError: () => toast.error(pageText.profile.addressPage.deleteAddressError)
  });

  const onSubmit = (data) => {
    const payload = {
      ...data,
      province_id: Number(data.province_id),
      city_id: Number(data.city_id),
    };
    addMutation.mutate(payload);
  };

  if (isAddressesLoading) return <div className="flex justify-center py-20"><span className="loading loading-spinner loading-lg text-primary"></span></div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-[90vw] mx-auto">
      
      {/* هدر صفحه */}
      <div className="flex justify-between items-center border-b border-slate-100 pb-4">
        <div>
          <h1 className="text-2xl font-black text-slate-800 flex items-center gap-2">
            <MapPin className="text-primary" /> {pageText.profile.addressPage.myAddresses}
          </h1>
          <p className="text-xs text-slate-400 mt-1">{pageText.profile.addressPage.orderAddressManagement}</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)} 
          className="btn btn-primary btn-sm gap-2 rounded-xl shadow-lg shadow-primary/20 hover:scale-105 transition-transform"
        >
          <Plus size={18} /> {pageText.profile.addressPage.addAddress}
        </button>
      </div>

      {/* لیست آدرس‌ها */}
      {addresses.length === 0 ? (
        <div className="text-center py-16 bg-slate-50 rounded-3xl border border-dashed border-slate-200">
          <MapPin size={48} className="mx-auto text-slate-300 mb-4" />
          <p className="text-slate-500 font-bold">{pageText.profile.addressPage.addressNotRegistered}</p>
          <button onClick={() => setIsModalOpen(true)} className="btn btn-ghost btn-sm mt-2 text-primary">{pageText.profile.addressPage.addingTheFirstAddress}</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {addresses.map((addr) => (
            <div key={addr.id} className="bg-white p-5 rounded-3xl border border-slate-200 relative group hover:shadow-md transition-shadow">
              <div className="flex items-start gap-3 mb-3">
                <div className="p-2 bg-orange-50 text-orange-500 rounded-xl">
                   <MapPin size={20} />
                </div>
                <div>
                  <span className="font-bold text-slate-800 block text-lg">
                    {addr.province_detail?.name}، {addr.city_detail?.name}
                  </span>
                  <p className="text-sm text-slate-500 mt-2 leading-relaxed bg-slate-50 p-2 rounded-lg border border-slate-100">
                    {addr.address}
                  </p>
                </div>
              </div>
              <div className="flex justify-between items-center pt-3 mt-2 border-t border-slate-50">
                <span className="text-xs text-slate-400 bg-slate-50 px-3 py-1 rounded-lg font-mono dir-ltr border border-slate-100">
                  ZIP: {addr.postal_code}
                </span>
                <button 
                  onClick={() => deleteMutation.mutate(addr.id)}
                  disabled={deleteMutation.isPending}
                  className="btn btn-ghost btn-xs text-error hover:bg-error/10"
                >
                  {deleteMutation.isPending ? <span className="loading loading-spinner loading-xs"></span> : <><Trash2 size={14} /> {globalText.delete}</>}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* مودال افزودن آدرس */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm transition-all">
          <div className="bg-white rounded-3xl w-full max-w-lg p-6 shadow-2xl animate-in zoom-in-95 duration-200 border border-slate-100">
            
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="font-black text-xl text-slate-800">{pageText.profile.addressPage.addNewAddress}</h3>
                <span className="text-xs text-slate-400">{pageText.profile.addressPage.enterFullAddressTitle}</span>
              </div>
              <button onClick={() => { setIsModalOpen(false); reset(); }} className="btn btn-circle btn-sm btn-ghost text-slate-500 hover:bg-slate-100"><X size={20}/></button>
            </div>
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              
              {/* انتخاب استان و شهر */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* استان */}
                <div className="form-control">
                  <label className="label text-xs font-bold text-slate-600">{pageText.profile.addressPage.province}</label>
                  <select 
                    className={`select select-bordered rounded-xl w-full ${errors.province_id ? 'select-error' : ''}`} 
                    {...register('province_id', { required: pageText.profile.addressPage.selectProvinceIsNessessary })}
                    disabled={isProvincesLoading}
                  >
                    <option value="">{pageText.profile.addressPage.selectAddress}</option>
                    {provinces?.map((p) => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                  {isProvincesLoading && <span className="text-[10px] text-primary mt-1">{pageText.profile.addressPage.loadingProvinces}</span>}
                </div>

                {/* شهر */}
                <div className="form-control">
                  <label className="label text-xs font-bold text-slate-600">{pageText.profile.addressPage.city}</label>
                  <select 
                    className={`select select-bordered rounded-xl w-full ${errors.city_id ? 'select-error' : ''}`} 
                    {...register('city_id', { required: pageText.profile.addressPage.selectCityIsNessessary })}
                    disabled={!selectedProvinceId || isCitiesLoading}
                  >
                    <option value="">
                      {!selectedProvinceId 
                        ? pageText.profile.addressPage.pleaseSelectProvinceFirst
                        : (isCitiesLoading ? pageText.profile.addressPage.loading : pageText.profile.addressPage.selectCity)}
                    </option>
                    {cities?.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* کد پستی */}
              {/* <div className="form-control">
                <label className="label text-xs font-bold text-slate-600">
                  کد پستی
                  <span className="text-[10px] font-normal text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">{pageText.profile.addressPage.onlyTen}</span>
                </label>
                <input 
                  type="text" 
                  maxLength={10} 
                  placeholder="xxxxxxxxxx"
                  className={`input input-bordered rounded-xl text-left dir-ltr font-mono tracking-widest ${errors.postal_code ? 'input-error' : ''}`} 
                  {...register('postal_code', { 
                    required: 'کد پستی الزامی است', 
                    minLength: { value: 10, message: 'کد پستی باید ۱۰ رقم باشد' },
                    pattern: { value: /^[0-9]+$/, message: 'فقط عدد وارد کنید' }
                  })} 
                />
                {errors.postal_code && <span className="text-error text-[10px] mt-1 flex items-center gap-1"><AlertCircle size={10}/> {errors.postal_code.message}</span>}
              </div> */}

              {/* آدرس دقیق */}
              <div className="form-control">
                <label className="label text-xs font-bold text-slate-600">{pageText.profile.addressPage.detailedAddress}</label>
                <textarea 
                  className={`textarea textarea-bordered rounded-xl h-24 leading-relaxed ${errors.address ? 'textarea-error' : ''}`} 
                  placeholder={pageText.profile.addressPage.detailedAddressPlaceHolder}
                  {...register('address', { required: pageText.profile.addressPage.detailedAddressIsNessessary })}
                ></textarea>
                 {errors.address && <span className="text-error text-[10px] mt-1 flex items-center gap-1"><AlertCircle size={10}/> {errors.address.message}</span>}
              </div>
              
              <div className="pt-2">
                <button 
                  type="submit" 
                  className="btn btn-primary w-full rounded-xl shadow-lg shadow-primary/20 text-base" 
                  disabled={addMutation.isPending}
                >
                  {addMutation.isPending ? <span className="loading loading-spinner"></span> : pageText.profile.addressPage.saveAddress}
                </button>
              </div>

            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AddressPage;