import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { verifySchema } from './schemas';
import { authService } from '../../services/authService';

const VerifyPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const emailFromUrl = searchParams.get('email');

  const { register, handleSubmit, setValue, formState: { errors } } = useForm({
    resolver: zodResolver(verifySchema),
  });

  useEffect(() => {
    if (emailFromUrl) {
      setValue('email', emailFromUrl);
    }
  }, [emailFromUrl, setValue]);

  const verifyMutation = useMutation({
    mutationFn: authService.verifyEmail,
    onSuccess: (data) => {
      // تغییر اصلی اینجاست: 
      // بررسی می‌کنیم اگر توکن توی ریسپانس بود، لاگین خودکار انجام بشه
      if (data?.access && data?.refresh) {
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        
        toast.success('خوش آمدید! حساب شما فعال شد.');
        // هدایت مستقیم به داشبورد (دیگه به لاگین نمیره)
        navigate('/'); 
      } else {
        // اگر بکند توکن نفرستاد (فقط پیام موفقیت داد)، چاره‌ای نیست جز رفتن به لاگین
        // اما طبق خواسته شما، فرض بر اینه که توکن میاد
        toast.success('حساب تایید شد.');
        navigate('/login');
      }
    },
    onError: (error) => {
      const msg = error.response?.data?.detail || 'کد وارد شده اشتباه است.';
      toast.error(msg);
    }
  });

  const onSubmit = (data) => {
    verifyMutation.mutate({ 
      email: emailFromUrl || data.email, 
      code: data.code 
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <h2 className="text-xl font-semibold text-center mb-2">تایید حساب کاربری</h2>
      <p className="text-sm text-center text-base-content/70 mb-6">
        کد تایید به ایمیل <span className="font-bold text-primary">{emailFromUrl}</span> ارسال شد.
      </p>

      {!emailFromUrl && (
        <div className="form-control">
          <label className="label"><span className="label-text">ایمیل</span></label>
          <input 
            type="email" 
            dir="ltr"
            className="input input-bordered w-full text-left"
            {...register('email')}
          />
        </div>
      )}

      <div className="form-control">
        <label className="label"><span className="label-text">کد تایید</span></label>
        <input 
          type="text" 
          maxLength={6} 
          placeholder="- - - -" 
          dir="ltr"
          className={`input input-bordered w-full text-center text-2xl tracking-[0.5em] font-mono ${errors.code ? 'input-error' : ''}`}
          {...register('code')}
        />
        {errors.code && <span className="text-error text-xs mt-1 text-center">{errors.code.message}</span>}
      </div>

      <button 
        type="submit" 
        className="btn btn-primary w-full mt-4"
        disabled={verifyMutation.isPending}
      >
        {verifyMutation.isPending ? <span className="loading loading-spinner"></span> : 'تایید و ورود'}
      </button>

      <div className="text-center mt-4 text-sm">
        <Link to="/register" className="text-secondary hover:underline">بازگشت به ثبت نام</Link>
      </div>
    </form>
  );
};

export default VerifyPage;