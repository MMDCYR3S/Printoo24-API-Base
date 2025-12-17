// src/app/features/auth/LoginPage.jsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query'; // 👈 ایمپورت useQueryClient
import toast from 'react-hot-toast';
import PasswordInput from '../../components/PasswordInput';
import { loginSchema } from './schemas';
import { authService } from '../../services/authService';

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient(); // 👈 گرفتن اینستنس کلاینت

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const loginMutation = useMutation({
    mutationFn: authService.login,
    onSuccess: async (data) => {
      // ۱. ذخیره توکن‌ها
      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);
      
      toast.success('ورود با موفقیت انجام شد');

      // 💥 ۲. پاکسازی کش پروفایل (قاتل باگ شما اینجاست!)
      // این خط باعث میشه useAdminAuth مجبور بشه دوباره از سرور استعلام بگیره
      await queryClient.invalidateQueries({ queryKey: ['profile-info'] });

      // ۳. ریدایرکت هوشمند
      // اگر کاربر میخواست بره ادمین و پرت شد بیرون، برش میگردونیم همونجا
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    },
    onError: (error) => {
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

      <div className="form-control">
        <label className="label"><span className="label-text">نام کاربری</span></label>
        <input 
          type="text" 
          dir="ltr"
          className={`input input-bordered w-full text-left ${errors.username ? 'input-error' : ''}`}
          {...register('username')}
        />
        {errors.username && <span className="text-error text-xs mt-1">{errors.username.message}</span>}
      </div>

      <div className="form-control">
        <label className="label"><span className="label-text">رمز عبور</span></label>
        <PasswordInput register={register} name="password" error={errors.password} />
        <label className="label">
           <Link to="/forgot-password" class="label-text-alt link link-hover text-primary">رمز عبور را فراموش کردید؟</Link>
        </label>
      </div>

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