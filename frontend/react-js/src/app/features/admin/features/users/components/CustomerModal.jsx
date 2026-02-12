import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  X, Save, User, Mail, Phone, Lock, 
  Briefcase, Shield, CheckCircle, AlertCircle, Wallet
} from 'lucide-react';
import { useCustomers } from '../../../hooks/useCustomers';
import { toast } from 'react-hot-toast';

// --- 1. تعریف اسکیما (Validation Rules) ---
const customerSchema = z.object({
  username: z.string().min(3, 'نام کاربری باید حداقل ۳ کاراکتر باشد'),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  email: z.string().email('فرمت ایمیل صحیح نیست').optional().or(z.literal('')),
  phone_number: z.string().min(10, 'شماره تماس معتبر نیست').optional().or(z.literal('')),
  
  // پسورد: در حالت ساخت اجباری، در ویرایش اختیاری
  password: z.string().optional().or(z.literal('')),
  
  company: z.string().optional(),
  bio: z.string().optional(),
  
  // دسترسی‌ها و وضعیت
  is_active: z.boolean().default(true),
  is_verified: z.boolean().default(false),
  is_staff: z.boolean().default(false),
  is_superuser: z.boolean().default(false),
});

// --- لیست سفید فیلدهای مجاز برای ارسال به بک‌اند ---
const ALLOWED_FIELDS = [
  'username', 'email', 'password', 'first_name', 'last_name', 
  'phone_number', 'company', 'bio', 
  'is_active', 'is_verified', 'is_staff', 'is_superuser'
];

const CustomerModal = ({ isOpen, onClose, initialData }) => {
  const isEdit = !!initialData;
  const { createMutation, updateMutation } = useCustomers();

  // --- 2. تنظیمات فرم ---
  const { 
    register, 
    handleSubmit, 
    reset, 
    watch,
    formState: { errors, isSubmitting } 
  } = useForm({
    resolver: zodResolver(customerSchema),
    defaultValues: {
      is_active: true,
      is_verified: false,
      is_staff: false,
      is_superuser: false
    }
  });

  const watchIsStaff = watch('is_staff');

  // --- 3. پر کردن فرم ---
  useEffect(() => {
    if (isOpen) {
      if (initialData) {
        // پر کردن فیلدها با داده‌های موجود
        reset({
          username: initialData.username || '',
          first_name: initialData.first_name || '',
          last_name: initialData.last_name || '',
          email: initialData.email || '',
          phone_number: initialData.phone_number || '',
          company: initialData.company || '',
          bio: initialData.bio || '',
          is_active: initialData.is_active ?? true,
          is_verified: initialData.is_verified ?? false,
          is_staff: initialData.is_staff ?? false,
          is_superuser: initialData.is_superuser ?? false,
          password: '', 
        });
      } else {
        // ریست برای ساخت جدید
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
          bio: ''
        });
      }
    }
  }, [isOpen, initialData, reset]);

  // --- 4. هندلر ثبت فرم (با فیلترینگ دقیق) ---
  const onSubmit = (data) => {
    // 1. ساخت Payload فقط از فیلدهای مجاز
    const payload = {};
    
    ALLOWED_FIELDS.forEach(field => {
      // اگر فیلد در دیتا وجود داشت، آن را کپی کن
      if (data[field] !== undefined && data[field] !== null) {
        payload[field] = data[field];
      }
    });

    // 2. لاجیک پسورد
    // اگر در حالت ویرایش هستیم و پسورد خالی است، آن را حذف کن تا تغییر نکند
    if (isEdit && !payload.password) {
      delete payload.password;
    }
    // اگر در حالت ساخت هستیم و پسورد خالی است، خطا بده
    if (!isEdit && !payload.password) {
      toast.error('برای کاربر جدید، رمز عبور الزامی است');
      return;
    }

    // 3. ارسال به سرور
    if (isEdit) {
      updateMutation.mutate({ id: initialData.id, data: payload }, {
        onSuccess: () => onClose()
      });
    } else {
      createMutation.mutate(payload, {
        onSuccess: () => onClose()
      });
    }
  };

  if (!isOpen) return null;

  return (
    <dialog className="modal modal-open backdrop-blur-sm bg-slate-900/40 z-50">
      <div className="modal-box w-11/12 max-w-4xl rounded-3xl p-0 overflow-hidden shadow-2xl bg-base-100">
        
        {/* Header */}
        <div className="flex justify-between items-center p-5 border-b border-base-200 bg-base-100/50 backdrop-blur sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <div className={`p-3 rounded-2xl ${isEdit ? 'bg-amber-50 text-amber-600' : 'bg-primary/10 text-primary'}`}>
              <User size={24} strokeWidth={1.5} />
            </div>
            <div>
              <h3 className="font-black text-xl text-base-content">
                {isEdit ? 'ویرایش اطلاعات کاربر' : 'تعریف کاربر جدید'}
              </h3>
              <p className="text-xs text-base-content/50 mt-1">
                {isEdit ? `در حال ویرایش: ${initialData.username}` : 'اطلاعات حساب و دسترسی‌ها را وارد کنید'}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="btn btn-circle btn-ghost btn-sm text-base-content/40 hover:text-error">
            <X size={20} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 md:p-8 overflow-y-auto max-h-[70vh]">
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* --- ستون راست: اطلاعات پایه --- */}
            <div className="space-y-6">
              <div className="flex items-center gap-2 text-sm font-bold text-primary mb-2 border-b border-primary/10 pb-2 w-fit">
                <User size={16}/> اطلاعات هویتی
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="form-control">
                  <label className="label text-xs font-bold text-base-content/70">نام</label>
                  <input {...register('first_name')} type="text" className="input input-bordered rounded-xl w-full" placeholder="مثال: علی" />
                </div>
                <div className="form-control">
                  <label className="label text-xs font-bold text-base-content/70">نام خانوادگی</label>
                  <input {...register('last_name')} type="text" className="input input-bordered rounded-xl w-full" placeholder="مثال: علوی" />
                </div>
              </div>

              <div className="form-control">
                <label className="label text-xs font-bold text-base-content/70">
                  نام کاربری <span className="text-error">*</span>
                </label>
                <div className="relative">
                  <input 
                    {...register('username')} 
                    type="text" 
                    className={`input input-bordered rounded-xl w-full dir-ltr pl-10 ${errors.username ? 'input-error' : ''}`}
                    placeholder="username"
                  />
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 text-base-content/30" size={18}/>
                </div>
                {errors.username && <span className="text-error text-[10px] mt-1">{errors.username.message}</span>}
              </div>

              <div className="form-control">
                <label className="label text-xs font-bold text-base-content/70">شماره موبایل</label>
                <div className="relative">
                  <input 
                    {...register('phone_number')} 
                    type="tel" 
                    className="input input-bordered rounded-xl w-full dir-ltr pl-10" 
                    placeholder="0912..."
                  />
                  <Phone className="absolute left-3 top-1/2 -translate-y-1/2 text-base-content/30" size={18}/>
                </div>
              </div>

              <div className="form-control">
                <label className="label text-xs font-bold text-base-content/70">ایمیل</label>
                <div className="relative">
                  <input 
                    {...register('email')} 
                    type="email" 
                    className={`input input-bordered rounded-xl w-full dir-ltr pl-10 ${errors.email ? 'input-error' : ''}`} 
                    placeholder="user@example.com"
                  />
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-base-content/30" size={18}/>
                </div>
                {errors.email && <span className="text-error text-[10px] mt-1">{errors.email.message}</span>}
              </div>

              {/* نمایش کیف پول فقط در حالت ویرایش */}
              {isEdit && (
                <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 flex justify-between items-center">
                  <div className="flex items-center gap-2 text-slate-500 text-sm">
                    <Wallet size={18}/> کیف پول
                  </div>
                  <div className="font-mono font-bold text-lg dir-ltr text-emerald-600">
                    {new Intl.NumberFormat('fa-IQ').format(initialData.wallet_balance || 0)} IQD
                  </div>
                </div>
              )}
            </div>

            {/* --- ستون چپ: امنیت و دسترسی --- */}
            <div className="space-y-6">
              
              {/* بخش رمز عبور */}
              <div>
                <div className="flex items-center gap-2 text-sm font-bold text-primary mb-4 border-b border-primary/10 pb-2 w-fit">
                  <Lock size={16}/> امنیت و نقش
                </div>
                
                <div className="form-control">
                  <label className="label text-xs font-bold text-base-content/70">
                    {isEdit ? 'تغییر رمز عبور (اختیاری)' : 'رمز عبور *'}
                  </label>
                  <input 
                    {...register('password')} 
                    type="password" 
                    autoComplete="new-password"
                    className={`input input-bordered rounded-xl w-full dir-ltr font-mono tracking-widest ${errors.password ? 'input-error' : ''}`}
                    placeholder={isEdit ? "********" : "حداقل ۶ کاراکتر"}
                  />
                  {errors.password && <span className="text-error text-[10px] mt-1">{errors.password.message}</span>}
                  {isEdit && <span className="text-[10px] text-base-content/40 mt-1">در صورتی که نمی‌خواهید رمز تغییر کند، این فیلد را خالی بگذارید.</span>}
                </div>
              </div>

              {/* بخش دسترسی‌ها */}
              <div className="bg-base-200/50 p-5 rounded-2xl space-y-4 border border-base-200">
                <h4 className="text-xs font-bold text-base-content/50 uppercase tracking-wider mb-2">سطوح دسترسی</h4>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle className={watch('is_active') ? "text-emerald-500" : "text-slate-300"} size={20}/>
                    <span className="text-sm font-medium">حساب کاربری فعال است</span>
                  </div>
                  <input type="checkbox" className="toggle toggle-success" {...register('is_active')} />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Shield className={watch('is_verified') ? "text-blue-500" : "text-slate-300"} size={20}/>
                    <span className="text-sm font-medium">هویت تایید شده (Verified)</span>
                  </div>
                  <input type="checkbox" className="toggle toggle-info" {...register('is_verified')} />
                </div>
                
                <div className="divider my-1"></div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Briefcase className={watch('is_staff') ? "text-purple-500" : "text-slate-300"} size={20}/>
                    <div>
                      <span className="text-sm font-medium block">دسترسی کارمند (Staff)</span>
                      <span className="text-[10px] text-base-content/40">دسترسی به پنل ادمین</span>
                    </div>
                  </div>
                  <input type="checkbox" className="toggle toggle-secondary" {...register('is_staff')} />
                </div>

                {watchIsStaff && (
                  <div className="flex items-center justify-between bg-warning/10 p-3 rounded-xl border border-warning/20 animate-in fade-in slide-in-from-top-2">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="text-warning" size={20}/>
                      <div>
                        <span className="text-sm font-bold text-warning-content block">مدیر کل (Superuser)</span>
                        <span className="text-[10px] text-warning-content/70">دسترسی کامل به تمام سیستم</span>
                      </div>
                    </div>
                    <input type="checkbox" className="toggle toggle-warning" {...register('is_superuser')} />
                  </div>
                )}
              </div>

              {/* اطلاعات تکمیلی */}
              <div className="form-control">
                 <label className="label text-xs font-bold text-base-content/70">نام شرکت / فروشگاه</label>
                 <input {...register('company')} type="text" className="input input-bordered rounded-xl w-full" />
              </div>

              <div className="form-control">
                 <label className="label text-xs font-bold text-base-content/70">بیوگرافی / یادداشت</label>
                 <textarea {...register('bio')} className="textarea textarea-bordered rounded-xl h-20 resize-none" placeholder="توضیحات کوتاه..."></textarea>
              </div>

            </div>
          </div>

        </form>

        {/* Footer Actions */}
        <div className="p-5 border-t border-base-200 bg-base-100 flex justify-end gap-3 sticky bottom-0 z-10">
          <button 
            type="button" 
            onClick={onClose} 
            className="btn btn-ghost hover:bg-base-200 rounded-xl"
            disabled={isSubmitting || updateMutation.isPending || createMutation.isPending}
          >
            انصراف
          </button>
          
          <button 
            onClick={handleSubmit(onSubmit)} 
            disabled={isSubmitting || updateMutation.isPending || createMutation.isPending}
            className="btn btn-primary px-8 rounded-xl shadow-lg shadow-primary/20"
          >
            {(isSubmitting || updateMutation.isPending || createMutation.isPending) ? (
              <span className="loading loading-spinner"></span>
            ) : (
              <>
                <Save size={18} />
                {isEdit ? 'ذخیره تغییرات' : 'ایجاد کاربر'}
              </>
            )}
          </button>
        </div>

      </div>
    </dialog>
  );
};

export default CustomerModal;