// admin.zip/features/users/components/CustomerAddressList.jsx

import React, { useEffect } from 'react';
import { useFieldArray, useFormContext, useWatch } from 'react-hook-form';
import { MapPin, Plus, Trash2, Building2 } from 'lucide-react';
import { useProvinces, useCities } from '../../../hooks/useLocations';

// --- کامپوننت سطر آدرس (ایزوله شده برای مدیریت شهرها) ---
const AddressRow = ({ index, remove }) => {
  const { register, control, setValue, formState: { errors } } = useFormContext();
  
  // دریافت مقدار فعلی استان برای همین سطر
  const provinceValue = useWatch({
    control,
    name: `addresses.${index}.province`
  });

  // استفاده از هوک شهرها (هر سطر استیت خودش را دارد)
  const { cities, setSelectedProvinceId, isLoading: isCitiesLoading } = useCities();

  // لود کردن شهرها وقتی استان تغییر می‌کند یا فرم لود می‌شود
  useEffect(() => {
    if (provinceValue) {
      // تبدیل به استرینگ برای اطمینان از سازگاری با هوک
      setSelectedProvinceId(String(provinceValue));
    }
  }, [provinceValue, setSelectedProvinceId]);

  // هندلر تغییر استان (شهر قبلی را پاک می‌کند)
  const handleProvinceChange = (e) => {
    const newVal = e.target.value;
    setValue(`addresses.${index}.province`, newVal);
    setValue(`addresses.${index}.city`, ''); // ریست شهر
  };

  const fieldErrors = errors.addresses?.[index] || {};

  return (
    <div className="bg-base-200/50 p-4 rounded-xl border border-base-200 space-y-4 relative group transition-all hover:border-base-300 hover:bg-base-200">
      
      <button
        type="button"
        onClick={() => remove(index)}
        className="btn btn-circle btn-ghost btn-xs absolute top-2 left-2 text-error opacity-0 group-hover:opacity-100 transition-opacity"
        title="حذف آدرس"
      >
        <Trash2 size={16} />
      </button>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* استان */}
        <div className="form-control">
          <label className="label text-xs font-bold text-base-content/70">استان</label>
          <ProvinceSelect 
            register={register} 
            name={`addresses.${index}.province`} 
            onChange={handleProvinceChange}
            error={fieldErrors.province}
          />
        </div>

        {/* شهر */}
        <div className="form-control">
          <label className="label text-xs font-bold text-base-content/70">شهر</label>
          <select 
            {...register(`addresses.${index}.city`)} 
            className={`select select-bordered select-sm w-full rounded-lg ${fieldErrors.city ? 'select-error' : ''}`}
            disabled={!provinceValue || isCitiesLoading}
          >
            <option value="">{isCitiesLoading ? 'در حال بارگذاری...' : 'انتخاب کنید'}</option>
            {cities?.map(city => (
              <option key={city.id} value={city.id}>{city.name}</option>
            ))}
          </select>
          {fieldErrors.city && <span className="text-error text-[10px] mt-1">{fieldErrors.city.message}</span>}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">


        {/* آدرس دقیق */}
        <div className="form-control col-span-3">
          <label className="label text-xs font-bold text-base-content/70">آدرس دقیق</label>
          <input 
            {...register(`addresses.${index}.address`)} 
            type="text" 
            className={`input input-bordered input-sm w-full rounded-lg ${fieldErrors.address ? 'input-error' : ''}`}
            placeholder="جزئیات آدرس..."
          />
          {fieldErrors.address && <span className="text-error text-[10px] mt-1">{fieldErrors.address.message}</span>}
        </div>
      </div>
    </div>
  );
};

// --- سلکت استان ---
const ProvinceSelect = ({ register, name, onChange, error }) => {
  const { provinces, isLoading } = useProvinces();
  return (
    <>
      <select 
        {...register(name, { onChange })} 
        className={`select select-bordered select-sm w-full rounded-lg ${error ? 'select-error' : ''}`}
        disabled={isLoading}
      >
        <option value="">انتخاب کنید</option>
        {provinces?.map(p => (
          <option key={p.id} value={p.id}>{p.name}</option>
        ))}
      </select>
      {error && <span className="text-error text-[10px] mt-1">{error.message}</span>}
    </>
  );
};

// --- کامپوننت اصلی ---
const CustomerAddressList = () => {
  const { control } = useFormContext();
  // اطمینان از وجود آرایه addresses
  const { fields, append, remove } = useFieldArray({
    control,
    name: "addresses"
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm font-bold text-primary mb-2 border-b border-primary/10 pb-2 w-fit">
        <MapPin size={16}/> آدرس‌ها
      </div>

      <div className="space-y-3">
        {fields.map((field, index) => (
          <AddressRow key={field.id} index={index} remove={remove} />
        ))}
      </div>

      {fields.length === 0 && (
        <div className="text-center py-6 bg-base-200/30 rounded-xl border border-dashed border-base-300">
          <Building2 className="mx-auto text-base-content/20 mb-2" size={28} />
          <p className="text-xs text-base-content/50">آدرسی ثبت نشده است</p>
        </div>
      )}

      <button
        type="button"
        onClick={() => append({ province: '', city: '', postal_code: '', address: '' })}
        className="btn btn-outline btn-primary btn-sm w-full border-dashed rounded-xl gap-2"
      >
        <Plus size={16} /> افزودن آدرس جدید
      </button>
    </div>
  );
};

export default CustomerAddressList;