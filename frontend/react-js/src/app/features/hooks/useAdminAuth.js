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
    staleTime: 1000 * 60 * 5,
  });

  // 🕵️‍♂️ بخش دیباگ (بعد از حل مشکل می‌تونی پاکش کنی)
  if (user) {
    console.log("🔥 [AdminAuth Debug] User Data:", user);
    console.log("❓ is_staff:", user.is_staff);
    console.log("❓ is_superuser:", user.is_superuser);
  } else if (isError) {
    console.error("❌ [AdminAuth Debug] Failed to fetch user profile");
  }

  // لاجیک تشخیص ادمین
  // نکته: ممکنه توی دیتابیس شما is_admin باشه، اینجا هر سه حالت رو چک می‌کنیم
  const isAdmin = user?.is_staff || user?.is_superuser || user?.is_admin; 

  return { 
    user, 
    isAdmin, 
    isLoading, 
    isAuthenticated: !!token && !isError 
  };
};