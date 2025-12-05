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
  const emailFromUrl = searchParams.get('email'); // خواندن ایمیل از URL

  const { register, handleSubmit, setValue, formState: { errors } } = useForm({
    resolver: zodResolver(verifySchema),
  });

  // اگر ایمیل در URL بود، آن را در فرم ست کن
  useEffect(() => {
    if (emailFromUrl) {
      setValue('email', emailFromUrl);
    }
  }, [emailFromUrl, setValue]);

  const verifyMutation = useMutation({
    mutationFn: authService.verifyEmail,
    onSuccess: (data) => {
      toast.success('حساب شما با موفقیت تایید شد! حالا وارد شوید.');
      navigate('/login');
    },
    onError: (error) => {
      const msg = error.response?.data?.detail || 'کد وارد شده اشتباه است.';
      toast.error(msg);
    }
  });

  const onSubmit = (data) => {
    // ارسال ایمیل (از URL یا فرم) به همراه کد به سرور
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

      {/* اگر ایمیل در URL نبود، اینپوت ایمیل را نشان بده (برای حالت دستی) */}
      {!emailFromUrl && (
        <div className="form-control">
          <label className="label"><span className="label-text">ایمیل</span></label>
          <input 
            type="email" 
            placeholder="example@mail.com"
            className="input input-bordered w-full text-left"
            {...register('email')}
          />
        </div>
      )}

      {/* ورودی کد */}
      <div className="form-control">
        <label className="label"><span className="label-text">کد تایید</span></label>
        <input 
          type="text" 
          maxLength={4} // محدودیت طول
          placeholder="- - - -" 
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
        {verifyMutation.isPending ? <span className="loading loading-spinner"></span> : 'تایید و ادامه'}
      </button>

      <div className="text-center mt-4 text-sm">
        <Link to="/register" className="text-secondary hover:underline">بازگشت به ثبت نام</Link>
      </div>
    </form>
  );
};

export default VerifyPage;