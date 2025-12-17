// src/app/hooks/useAdminAuth.js
import { useQuery } from '@tanstack/react-query';
import { profileService } from '../../services/profileService';

export const useAdminAuth = () => {
  const token = localStorage.getItem('accessToken');

  const { data: user, isLoading, isError } = useQuery({
    queryKey: ['profile-info'],
    queryFn: profileService.getProfileInfo,
    enabled: !!token,
    retry: false,
    staleTime: 1000 * 60 * 5, // 5 دقیقه
    // ✅ این خط طلاییه: دیتای اولیه رو از لوکال استوریج می‌خونه
    initialData: () => {
      const storedUser = localStorage.getItem('userData');
      return storedUser ? JSON.parse(storedUser) : undefined;
    },
  });

  // لاجیک تشخیص ادمین
  const isAdmin = user?.is_staff || user?.is_superuser;

  return { 
    user, 
    isAdmin, 
    // ✅ اگر دیتای اولیه باشه، دیگه isLoading ترو نمیشه و صفحه سفید نمیاد
    isLoading: isLoading && !user, 
    isAuthenticated: !!token && !isError 
  };
};