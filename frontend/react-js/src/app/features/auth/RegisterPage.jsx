import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { registerSchema } from './schemas';
import { authService } from '../../services/authService';
import PasswordInput from '../../components/PasswordInput'; // ایمپورت کامپوننت جدید

const RegisterPage = () => {
  const navigate = useNavigate();

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(registerSchema),
  });

  const registerMutation = useMutation({
    mutationFn: authService.register,
    onSuccess: (data, variables) => {
      toast.success('ثبت نام انجام شد! کد تایید ارسال گردید.');
      // فرض بر این است که بک‌اند ایمیل را برمی‌گرداند، اگر نه از ورودی می‌خوانیم
      const email = data?.email || variables.email;
      navigate(`/verify?email=${email}`);
    },
    onError: (error) => {
      // حالا که ارور دقیق را می‌دانیم، بهتر نمایش می‌دهیم
      const data = error.response?.data;
      if (data?.username) toast.error(`نام کاربری: ${data.username[0]}`);
      else if (data?.email) toast.error(`ایمیل: ${data.email[0]}`);
      else if (data?.password) toast.error(`رمز عبور: ${data.password[0]}`);
      else if (data?.password_2) toast.error(`تکرار رمز: ${data.password_2[0]}`);
      else toast.error('خطا در ثبت نام. لطفاً ورودی‌ها را چک کنید.');
    }
  });

  const onSubmit = (data) => {
    // نکته مهم: حالا data دقیقا شامل {username, email, password, password_2} است
    // که دقیقا همان چیزی است که بک‌اند می‌خواهد. پس مستقیم می‌فرستیم.
    registerMutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <h2 className="text-xl font-semibold text-center mb-4">ایجاد حساب جدید</h2>

      {/* ایمیل */}
      <div className="form-control">
        <label className="label"><span className="label-text">ایمیل</span></label>
        <input 
          type="email" 
          dir="ltr"
          className={`input input-bordered w-full text-left ${errors.email ? 'input-error' : ''}`}
          {...register('email')}
        />
        {errors.email && <span className="text-error text-xs">{errors.email.message}</span>}
      </div>

      {/* نام کاربری */}
      <div className="form-control">
        <label className="label"><span className="label-text">نام کاربری</span></label>
        <input 
          type="text" 
          dir="ltr"
          className={`input input-bordered w-full text-left ${errors.username ? 'input-error' : ''}`}
          {...register('username')}
        />
        {errors.username && <span className="text-error text-xs">{errors.username.message}</span>}
      </div>

      {/* رمز عبور */}
      <div className="form-control">
        <label className="label"><span className="label-text">رمز عبور</span></label>
        <PasswordInput 
          register={register} 
          name="password" 
          error={errors.password} 
        />
      </div>

      {/* تکرار رمز عبور (با نام جدید password_2) */}
      <div className="form-control">
        <label className="label"><span className="label-text">تکرار رمز عبور</span></label>
        <PasswordInput 
          register={register} 
          name="password_2" 
          error={errors.password_2} 
          placeholder="تکرار رمز عبور"
        />
      </div>

      <button 
        type="submit" 
        className="btn btn-secondary w-full mt-4"
        disabled={registerMutation.isPending}
      >
        {registerMutation.isPending ? <span className="loading loading-spinner"></span> : 'ثبت نام'}
      </button>

      <div className="text-center mt-4 text-sm">
        قبلاً ثبت نام کرده‌اید؟ <Link to="/login" className="text-primary font-bold hover:underline">وارد شوید</Link>
      </div>
    </form>
  );
};

export default RegisterPage;