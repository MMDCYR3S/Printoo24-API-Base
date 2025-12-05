import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import PasswordInput from '../../components/PasswordInput';

import { loginSchema } from './schemas'; // اسکیمایی که قبلا ساختیم
import { authService } from '../../services/authService';

const LoginPage = () => {
  const navigate = useNavigate();

  // 1. تنظیم هوک فرم با Zod
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
  });

  // 2. تنظیم Mutation برای مدیریت درخواست به سرور
  const loginMutation = useMutation({
    mutationFn: authService.login,
    onSuccess: (data) => {
      // ذخیره توکن‌ها
      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);
      
      toast.success('ورود با موفقیت انجام شد');
      navigate('/'); // هدایت به داشبورد
    },
    onError: (error) => {
      // مدیریت خطای بکند
      const message = error.response?.data?.detail || 'نام کاربری یا رمز عبور اشتباه است';
      toast.error(message);
    }
  });

  const onSubmit = (data) => {
    loginMutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <h2 className="text-xl font-semibold text-center mb-4">ورود به حساب کاربری</h2>

      {/* فیلد نام کاربری */}
      <div className="form-control">
        <label className="label">
          <span className="label-text">نام کاربری</span>
        </label>
        <input 
          type="text" 
          placeholder="نام کاربری خود را وارد کنید" 
          className={`input input-bordered w-full ${errors.username ? 'input-error' : ''}`}
          {...register('username')}
        />
        {errors.username && <span className="text-error text-xs mt-1">{errors.username.message}</span>}
      </div>

      {/* فیلد رمز عبور */}
      <div className="form-control">
        <label className="label">
          <span className="label-text">رمز عبور</span>
        </label>
  <PasswordInput 
          register={register} 
          name="password" 
          error={errors.password}
        />
        {errors.password && <span className="text-error text-xs mt-1">{errors.password.message}</span>}
        <label className="label">
           <Link to="/forgot-password" class="label-text-alt link link-hover text-primary">رمز عبور را فراموش کردید؟</Link>
        </label>
      </div>

      {/* دکمه ورود */}
      <button 
        type="submit" 
        className="btn btn-primary w-full mt-4"
        disabled={loginMutation.isPending}
      >
        {loginMutation.isPending ? <span className="loading loading-spinner"></span> : 'ورود'}
      </button>

      <div className="text-center mt-4 text-sm">
        حساب کاربری ندارید؟ <Link to="/register" className="text-secondary font-bold hover:underline">ثبت نام کنید</Link>
      </div>
    </form>
  );
};

export default LoginPage;
