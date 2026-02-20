import { useQuery } from '@tanstack/react-query';
import { adminOrderService } from '../services/adminOrderService';

export const useOrderStatuses = () => {
  const { data: statuses = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['admin-order-statuses'],
    queryFn: adminOrderService.getStatuses,
    staleTime: 1000 * 60 * 60 * 24, // کش ۲۴ ساعته (وضعیت‌ها به ندرت تغییر می‌کنند)
    cacheTime: 1000 * 60 * 60 * 24,
    retry: 2, // دو بار تلاش در صورت خطا
  });

  // یک تابع کمکی برای پیدا کردن رنگ یا مشخصات وضعیت بر اساس کد
  const getStatusByCode = (code) => {
    return statuses.find((s) => s.internal_code === code || s.name === code);
  };

  return {
    statuses,
    isLoading,
    isError,
    refetch,
    getStatusByCode
  };
};