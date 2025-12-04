import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { registerSchema } from './schemas';
import { authService } from '../../services/authService';

const RegisterPage = () => {
  const navigate = useNavigate();

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(registerSchema),
  });

  const registerMutation = useMutation({
    mutationFn: authService.register,
    onSuccess: (data, variables) => {
      toast.success('ثبت نام انجام شد! کد تایید ارسال گردید.');
      // انتقال ایمیل کاربر به صفحه وریفای برای راحتی
      navigate(`/verify?email=${variables.email}`); 
    },
    onError: (error) => {
      // نمایش خطاهای ولیدیشن سرور (مثلا نام کاربری تکراری)
      const errorMsg = error.response?.data?.username ? 'این نام کاربری قبلا گرفته شده است' : 'خطا در ثبت نام';
      toast.error(errorMsg);
    }
  });

  const onSubmit = (data) => {
    // فیلد confirmPassword فقط برای فرانت بود، به بکند ارسالش نمی‌کنیم
    const { confirmPassword, ...serverData } = data; 
    registerMutation.mutate(serverData);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <h2 className="text-xl font-semibold text-center mb-4">ایجاد حساب جدید</h2>

      {/* ایمیل */}
      <div className="form-control">
        <label className="label"><span className="label-text">ایمیل</span></label>
        <input 
          type="email" 
          className={`input input-bordered w-full ${errors.email ? 'input-error' : ''}`}
          {...register('email')}
        />
        {errors.email && <span className="text-error text-xs">{errors.email.message}</span>}
      </div>

      {/* نام کاربری */}
      <div className="form-control">
        <label className="label"><span className="label-text">نام کاربری</span></label>
        <input 
          type="text" 
          className={`input input-bordered w-full ${errors.username ? 'input-error' : ''}`}
          {...register('username')}
        />
        {errors.username && <span className="text-error text-xs">{errors.username.message}</span>}
      </div>

      {/* رمز عبور */}
      <div className="form-control">
        <label className="label"><span className="label-text">رمز عبور</span></label>
        <input 
          type="password" 
          className={`input input-bordered w-full ${errors.password ? 'input-error' : ''}`}
          {...register('password')}
        />
        {errors.password && <span className="text-error text-xs">{errors.password.message}</span>}
      </div>

      {/* تکرار رمز عبور */}
      <div className="form-control">
        <label className="label"><span className="label-text">تکرار رمز عبور</span></label>
        <input 
          type="password" 
          className={`input input-bordered w-full ${errors.confirmPassword ? 'input-error' : ''}`}
          {...register('confirmPassword')}
        />
        {errors.confirmPassword && <span className="text-error text-xs">{errors.confirmPassword.message}</span>}
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
