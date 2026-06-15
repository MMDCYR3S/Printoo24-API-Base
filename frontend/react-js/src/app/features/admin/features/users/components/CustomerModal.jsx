// admin.zip/features/users/components/CustomerModal.jsx

import React, { useEffect } from 'react';
import { useForm, FormProvider } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  X, Save, User, Mail, Phone, Lock, 
  Briefcase, Shield, CheckCircle, AlertCircle, Wallet
} from 'lucide-react';
import { useCustomers } from '../../../hooks/useCustomers';
import { customerService } from '../../../services/customerService';
import { toast } from 'react-hot-toast';
import CustomerAddressList from './CustomerAddressList'; // اطمینان از مسیر صحیح

// --- اسکیما ---
const customerSchema = z.object({
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  email: z.string().email('فرمت ایمیل اشتباه است').optional().or(z.literal('')),
  phone_number: z.string().min(10, 'شماره معتبر نیست').optional().or(z.literal('')),
  password: z.string().optional().or(z.literal('')),
  company: z.string().optional(),
  bio: z.string().optional(),
  
  is_active: z.boolean().default(true),
  is_verified: z.boolean().default(false),
  is_staff: z.boolean().default(false),
  is_superuser: z.boolean().default(false),

  // مدیریت آدرس‌ها
  addresses: z.array(z.object({
    id: z.number().optional(),
    province: z.coerce.number().min(1, 'استان الزامی است'),
    city: z.coerce.number().min(1, 'شهر الزامی است'),
    postal_code: z.string().optional().or(z.literal('')),
    address: z.string().min(5, 'آدرس دقیق الزامی است')
  })).optional()
});

const ALLOWED_FIELDS = [
  'username', 'email', 'password', 'first_name', 'last_name', 
  'phone_number', 'company', 'bio', 
  'is_active', 'is_verified', 'is_staff', 'is_superuser',
  'addresses'
];

const CustomerModal = ({ isOpen, onClose, initialData }) => {
  const isEdit = !!initialData;
  const { createMutation, updateMutation } = useCustomers();

  // --- دریافت اطلاعات کامل (شامل آدرس‌ها) ---
  const { data: fullUserData, isLoading: isLoadingDetails } = useQuery({
    queryKey: ['customer-details', initialData?.id],
    queryFn: () => customerService.getById(initialData.id),
    enabled: isEdit && isOpen,
    staleTime: 0
  });

  const methods = useForm({
    resolver: zodResolver(customerSchema),
    defaultValues: {
      is_active: true,
      addresses: []
    }
  });

  const { register, handleSubmit, reset, watch, formState: { errors, isSubmitting } } = methods;
  const watchIsStaff = watch('is_staff');

  // --- پر کردن فرم ---
  useEffect(() => {
    if (isOpen) {
      if (isEdit) {
        // اولویت با دیتای کامل است، اگر نبود دیتای اولیه
        const data = fullUserData || initialData;
        
        reset({
          username: data.username || '',
          first_name: data.first_name || '',
          last_name: data.last_name || '',
          email: data.email || '',
          phone_number: data.phone_number || '',
          company: data.company || '',
          bio: data.bio || '',
          is_active: data.is_active ?? true,
          is_verified: data.is_verified ?? false,
          is_staff: data.is_staff ?? false,
          is_superuser: data.is_superuser ?? false,
          password: '',
          // تبدیل null به '' برای جلوگیری از وارنینگ ری‌اکت
          addresses: (data.addresses || []).map(addr => ({
            ...addr,
            postal_code: addr.postal_code || '',
            address: addr.address || ''
          }))
        });
      } else {
        reset({
          is_active: true,
          is_verified: false,
          is_staff: false,
          is_superuser: false,
          username: '',
          password: '',
          first_name: '',
          last_name: '',
          email: '',
          phone_number: '',
          company: '',
          bio: '',
          addresses: []
        });
      }
    }
  }, [isOpen, initialData, fullUserData, isEdit, reset]);

  const onSubmit = (data) => {
    const payload = {};
    ALLOWED_FIELDS.forEach(field => {
      if (data[field] !== undefined && data[field] !== null) {
        payload[field] = data[field];
      }
    });

    if (isEdit && !payload.password) delete payload.password;
    if (!isEdit && !payload.password) {
      toast.error('رمز عبور الزامی است');
      return;
    }

    if (isEdit) {
      updateMutation.mutate({ id: initialData.id, data: payload }, { onSuccess: onClose });
    } else {
      createMutation.mutate(payload, { onSuccess: onClose });
    }
  };

  if (!isOpen) return null;

  return (
    <dialog className="modal modal-open backdrop-blur-sm bg-slate-900/40 z-50">
      <div className="modal-box w-11/12 max-w-4xl rounded-3xl p-0 overflow-hidden shadow-2xl bg-base-100 relative">
        
        {/* Loading Overlay */}
        {isEdit && isLoadingDetails && (
          <div className="absolute inset-0 z-50 bg-base-100/90 flex flex-col items-center justify-center backdrop-blur-sm">
             <span className="loading loading-spinner loading-lg text-primary"></span>
             <span className="text-sm font-medium text-base-content/70 mt-3">در حال دریافت اطلاعات کامل کاربر...</span>
          </div>
        )}

        {/* Header */}
        <div className="flex justify-between items-center p-5 border-b border-base-200 bg-base-100 sticky top-0 z-20">
          <div className="flex items-center gap-3">
            <div className={`p-3 rounded-2xl ${isEdit ? 'bg-amber-50 text-amber-600' : 'bg-primary/10 text-primary'}`}>
              <User size={24} />
            </div>
            <div>
              <h3 className="font-black text-xl text-base-content">
                {isEdit ? 'ویرایش کاربر' : 'کاربر جدید'}
              </h3>
              <p className="text-xs text-base-content/50 mt-1">
                {isEdit ? initialData.username : 'اطلاعات را وارد کنید'}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="btn btn-circle btn-ghost btn-sm text-base-content/40 hover:text-error">
            <X size={20} />
          </button>
        </div>

        {/* Form Body */}
        <FormProvider {...methods}>
          <form onSubmit={handleSubmit(onSubmit)} className="p-6 md:p-8 overflow-y-auto max-h-[70vh]">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              
              {/* ستون راست */}
              <div className="space-y-6">
                <div className="flex items-center gap-2 text-sm font-bold text-primary mb-2 border-b border-primary/10 pb-2 w-fit">
                  <User size={16}/> مشخصات
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="form-control">
                    <label className="label text-xs font-bold text-base-content/70">نام</label>
                    <input {...register('first_name')} className="input input-bordered rounded-xl w-full" />
                  </div>
                  <div className="form-control">
                    <label className="label text-xs font-bold text-base-content/70">نام خانوادگی</label>
                    <input {...register('last_name')} className="input input-bordered rounded-xl w-full" />
                  </div>
                </div>

                {/* <div className="form-control">
                  <label className="label text-xs font-bold text-base-content/70">نام کاربری *</label>
                  <input {...register('username')} className={`input input-bordered rounded-xl w-full dir-ltr ${errors.username ? 'input-error' : ''}`} />
                  {errors.username && <span className="text-error text-[10px] mt-1">{errors.username.message}</span>}
                </div> */}

                <div className="form-control">
                  <label className="label text-xs font-bold text-base-content/70">موبایل</label>
                  <input {...register('phone_number')} className="input input-bordered rounded-xl w-full dir-ltr" />
                </div>



                {isEdit && (
                  <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 flex justify-between items-center">
                    <div className="flex items-center gap-2 text-slate-500 text-sm"><Wallet size={18}/> موجودی</div>
                    <div className="font-mono font-bold text-lg dir-ltr text-emerald-600">
                      {new Intl.NumberFormat('fa-IQ').format((fullUserData || initialData).wallet_balance || 0)} IQD
                    </div>
                  </div>
                )}
                
                <div className="divider"></div>
                
                {/* --- لیست آدرس‌ها (اینجا لود می‌شود) --- */}
                <CustomerAddressList />
              </div>

              {/* ستون چپ */}
              <div className="space-y-6">
                <div>
                  <div className="flex items-center gap-2 text-sm font-bold text-primary mb-4 border-b border-primary/10 pb-2 w-fit">
                    <Lock size={16}/> دسترسی و امنیت
                  </div>
                  <div className="form-control">
                    <label className="label text-xs font-bold text-base-content/70">{isEdit ? 'تغییر رمز (اختیاری)' : 'رمز عبور *'}</label>
                    <input {...register('password')} type="password" autoComplete="new-password" className="input input-bordered rounded-xl w-full dir-ltr font-mono tracking-widest" placeholder={isEdit ? "********" : "حداقل ۶ رقم"} />
                    {errors.password && <span className="text-error text-[10px] mt-1">{errors.password.message}</span>}
                  </div>
                </div>

                <div className="bg-base-200/50 p-5 rounded-2xl space-y-4 border border-base-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle className={watch('is_active') ? "text-emerald-500" : "text-slate-300"} size={20}/>
                      <span className="text-sm font-medium">حساب فعال</span>
                    </div>
                    <input type="checkbox" className="toggle toggle-success" {...register('is_active')} />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Shield className={watch('is_verified') ? "text-blue-500" : "text-slate-300"} size={20}/>
                      <span className="text-sm font-medium">تایید هویت</span>
                    </div>
                    <input type="checkbox" className="toggle toggle-info" {...register('is_verified')} />
                  </div>
                  <div className="divider my-1"></div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Briefcase className={watch('is_staff') ? "text-purple-500" : "text-slate-300"} size={20}/>
                      <span className="text-sm font-medium">کارمند (Staff)</span>
                    </div>
                    <input type="checkbox" className="toggle toggle-secondary" {...register('is_staff')} />
                  </div>
                  {watchIsStaff && (
                    <div className="flex items-center justify-between bg-warning/10 p-3 rounded-xl border border-warning/20">
                      <div className="flex items-center gap-2">
                        <AlertCircle className="text-warning" size={20}/>
                        <span className="text-sm font-bold text-warning-content">مدیر کل (Superuser)</span>
                      </div>
                      <input type="checkbox" className="toggle toggle-warning" {...register('is_superuser')} />
                    </div>
                  )}
                </div>

                <div className="form-control">
                   <label className="label text-xs font-bold text-base-content/70">شرکت</label>
                   <input {...register('company')} className="input input-bordered rounded-xl w-full" />
                </div>
                <div className="form-control">
                   <label className="label text-xs font-bold text-base-content/70">بیوگرافی</label>
                   <textarea {...register('bio')} className="textarea textarea-bordered rounded-xl h-20 resize-none"></textarea>
                </div>
              </div>
            </div>
          </form>
        </FormProvider>

        {/* Footer */}
        <div className="p-5 border-t border-base-200 bg-base-100 flex justify-end gap-3 sticky bottom-0 z-20">
          <button type="button" onClick={onClose} className="btn btn-ghost hover:bg-base-200 rounded-xl" disabled={isSubmitting}>انصراف</button>
          <button onClick={handleSubmit(onSubmit)} disabled={isSubmitting} className="btn btn-primary px-8 rounded-xl shadow-lg">
            {(isSubmitting || updateMutation.isPending || createMutation.isPending) ? <span className="loading loading-spinner"></span> : <><Save size={18} /> {isEdit ? 'ذخیره' : 'ایجاد'}</>}
          </button>
        </div>
      </div>
    </dialog>
  );
};

export default CustomerModal;