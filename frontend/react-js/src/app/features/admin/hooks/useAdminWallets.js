// src/app/features/admin/customers/hooks/useAdminWallets.js
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { adminWalletService } from '../services/adminWalletService';
import { toast } from 'react-hot-toast';

export const useAdminWallets = () => {
  const queryClient = useQueryClient();

  const adjustBalanceMutation = useMutation({
    // تغییر: حالا کل payload مستقیم پاس داده میشه به سرویس
    mutationFn: (payload) => adminWalletService.adjustBalance(payload),
    
    onSuccess: (data) => {
      const actionText = data?.action_type === 'deposit' ? 'واریز' : 'برداشت';
      toast.success(`${actionText} با موفقیت ثبت شد`, {
        icon: '💰',
        style: { borderRadius: '10px', background: '#333', color: '#fff' },
      });

      // آپدیت کردن لیست کاربران برای نمایش موجودی جدید
      queryClient.invalidateQueries(['admin-customers']);
      queryClient.invalidateQueries(['admin-wallets']);
    },
    onError: (err) => {
      const msg = err?.response?.data?.message || 'خطا در انجام تراکنش';
      toast.error(msg);
    }
  });

  return {
    adjustBalanceMutation
  };
};