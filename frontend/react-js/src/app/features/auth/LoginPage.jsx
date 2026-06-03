// src/app/features/auth/LoginPage.jsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import PasswordInput from '../../components/PasswordInput';
import { loginSchema } from './schemas';
import { authService } from '../../services/authService';

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const loginMutation = useMutation({
    mutationFn: authService.login,
    onSuccess: (data) => {
      const accessToken = data.tokens?.access;
      const refreshToken = data.tokens?.refresh;

      if (!accessToken) {
        toast.error(" هەڵەیەک ڕوویدا، تکایە دووبارە هەوڵ بدەرەوە ");
        return;
      }

      // 1. ذخیره توکن‌ها
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      
      // 2. ذخیره اطلاعات کاربر و ریدایرکت هوشمند
      let defaultPath = '/';

      if (data.user) {
        localStorage.setItem('userData', JSON.stringify(data.user));
        localStorage.setItem('userId', data.user.id);
        queryClient.setQueryData(['profile-info'], data.user);

        const isStaff = data.user.is_staff === true || data.user.is_staff === "true";
        const isSuperuser = data.user.is_superuser === true || data.user.is_superuser === "true";
        
        if (isStaff || isSuperuser) {
          defaultPath = '/admin';
        }
      }

      // 🛑 راهکار قطعی رفع مشکل محو نشدن Toast
      const toastId = toast.success(' بە سەرکەوتوویی چوویتە ژوورەوە ');
      
      setTimeout(() => {
        toast.dismiss(toastId); // بستن اجباری و هدفمند همین پیام
      }, 2000);

      const from = location.state?.from?.pathname || defaultPath;
      navigate(from, { replace: true });
    },
    onError: (error) => {
      const message = error.response?.data?.detail ;
      toast.error(message);
    }
  });

  const onSubmit = (data) => {
    loginMutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <h2 className="text-xl font-semibold text-center mb-4"> چوونەژوورەوە / تۆمارکردن </h2>
      <p className="text-sm text-base-content/70 mt-2"> دڵنیابە لە دروستی ژمارەی مۆبایلەکەت، چونکە هەموو زانیارییەکانی داواکاریەکانت لە ڕێگەی ئەم ژمارەیە دەگەیەنرێت </p>

      
      <div className="form-control">
        {/* <label className="label"><span className="label-text"> شماره تلفن </span></label> */}
        <input 
          type="text" 
          dir="ltr"
          placeholder="09123456789"
          className={`input input-bordered w-full text-left ${errors.phone_number ? 'input-error' : ''}`}
          {...register('phone_number')}
        />
        {errors.phone_number && <span className="text-error text-xs mt-1">{errors.phone_number.message}</span>}
      </div>

      <div className="form-control">
        <label className="label"><span className="label-text"> وشەی نهێنی </span></label>
        <PasswordInput register={register} name="password" error={errors.password} />
        <label className="label">
           <Link to="/forgot-password" className="label-text-alt link link-hover text-primary">
           </Link>
        </label>
      </div>

      <button 
        type="submit" 
        className="btn btn-primary w-full mt-4"
        disabled={loginMutation.isPending}
      >
        {loginMutation.isPending ? <span className="loading loading-spinner"></span> : 'چوونەژوورەوە'}
      </button>

    </form>
  );
};

export default LoginPage;