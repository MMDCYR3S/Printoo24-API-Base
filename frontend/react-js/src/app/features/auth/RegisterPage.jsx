// src/app/features/auth/RegisterPage.jsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { registerSchema } from './schemas';
import { authService } from '../../services/authService';
import PasswordInput from '../../components/PasswordInput';

const RegisterPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(registerSchema),
  });

  // 1. میوتیشن برای ورود خودکار (بعد از موفقیت ثبت نام)
  const loginMutation = useMutation({
    mutationFn: authService.login,
    onSuccess: (data) => {
      const accessToken = data.tokens?.access;
      const refreshToken = data.tokens?.refresh;

      if (accessToken) {
        localStorage.setItem('accessToken', accessToken);
        localStorage.setItem('refreshToken', refreshToken);
        
        let defaultPath = '/';
        if (data.user) {
          localStorage.setItem('userData', JSON.stringify(data.user));
          localStorage.setItem('userId', data.user.id);
          queryClient.setQueryData(['profile-info'], data.user);

          const isStaff = data.user.is_staff === true || data.user.is_staff === "true";
          const isSuperuser = data.user.is_superuser === true || data.user.is_superuser === "true";
          if (isStaff || isSuperuser) defaultPath = '/admin';
        }
        
        // 🛑 پاکسازی دستی و ریدایرکت آنی
        const loginToastId = toast.success('ورود موفقیت‌آمیز');
        setTimeout(() => toast.dismiss(loginToastId), 2000);
        
        navigate(defaultPath, { replace: true });
      }
    }
  });

  // 2. میوتیشن ثبت نام اصلی
  const registerMutation = useMutation({
    mutationFn: authService.register,
    onSuccess: (data, variables) => {
      const regToastId = toast.success('ثبت نام انجام شد! در حال ورود...');
      setTimeout(() => toast.dismiss(regToastId), 2000);

      loginMutation.mutate({
        phone_number: variables.phone_number,
        password: variables.password
      });
    },
    onError: (error) => {
      const data = error.response?.data;
      if (data?.phone_number) toast.error(`شماره تلفن: ${data.phone_number[0]}`);
      else if (data?.first_name) toast.error(`نام: ${data.first_name[0]}`);
      else if (data?.last_name) toast.error(`نام خانوادگی: ${data.last_name[0]}`);
      else if (data?.password) toast.error(`رمز عبور: ${data.password[0]}`);
      else if (data?.password_2) toast.error(`تکرار رمز: ${data.password_2[0]}`);
      else toast.error('خطا در ثبت نام. لطفاً ورودی‌ها را چک کنید.');
    }
  });

  const onSubmit = (data) => {
    registerMutation.mutate({
      phone_number: data.phone_number,
      first_name: data.first_name,
      last_name: data.last_name,
      password: data.password,
      password_2: data.password_2
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <h2 className="text-xl font-semibold text-center mb-4">ایجاد حساب جدید</h2>

      <div className="grid grid-cols-2 gap-2">
        {/* نام */}
        <div className="form-control">
          <label className="label"><span className="label-text">نام</span></label>
          <input 
            type="text" 
            className={`input input-bordered w-full ${errors.first_name ? 'input-error' : ''}`}
            {...register('first_name')}
          />
          {errors.first_name && <span className="text-error text-xs mt-1">{errors.first_name.message}</span>}
        </div>

        {/* نام خانوادگی */}
        <div className="form-control">
          <label className="label"><span className="label-text">نام خانوادگی</span></label>
          <input 
            type="text" 
            className={`input input-bordered w-full ${errors.last_name ? 'input-error' : ''}`}
            {...register('last_name')}
          />
          {errors.last_name && <span className="text-error text-xs mt-1">{errors.last_name.message}</span>}
        </div>
      </div>

      {/* شماره تلفن */}
      <div className="form-control">
        <label className="label"><span className="label-text">شماره تلفن</span></label>
        <input 
          type="text" 
          dir="ltr"
          placeholder="09..."
          className={`input input-bordered w-full text-left ${errors.phone_number ? 'input-error' : ''}`}
          {...register('phone_number')}
        />
        {errors.phone_number && <span className="text-error text-xs mt-1">{errors.phone_number.message}</span>}
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

      {/* تکرار رمز عبور */}
      <div className="form-control">
        <label className="label"><span className="label-text">تکرار رمز عبور</span></label>
        <PasswordInput 
          register={register} 
          name="password_2" 
          error={errors.password_2} 
          placeholder="********"
        />
      </div>

      <button 
        type="submit" 
        className="btn btn-secondary w-full mt-4"
        disabled={registerMutation.isPending || loginMutation.isPending}
      >
        {(registerMutation.isPending || loginMutation.isPending) ? 
          <span className="loading loading-spinner"></span> : 'ثبت نام'}
      </button>

      <div className="text-center mt-4 text-sm">
        قبلاً ثبت نام کرده‌اید؟ <Link to="/login" className="text-primary font-bold hover:underline">وارد شوید</Link>
      </div>
    </form>
  );
};

export default RegisterPage;