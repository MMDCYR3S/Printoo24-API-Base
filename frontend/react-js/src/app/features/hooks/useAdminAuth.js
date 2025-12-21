import { useQuery } from '@tanstack/react-query';
import { profileService } from '../../services/profileService';

export const useAdminAuth = () => {
  const token = localStorage.getItem('accessToken');

  const { data: user, isLoading, isError } = useQuery({
    queryKey: ['profile-info'],
    queryFn: profileService.getProfileInfo,
    enabled: !!token,
    retry: 1, // فقط یک بار تلاش کنه
    staleTime: 0, // همیشه دیتای تازه بگیره
  });

  const isAdmin = !!(user?.is_staff || user?.is_superuser);

  return { 
    user, 
    isAdmin, 
    isLoading: isLoading && !!token, 
    isAuthenticated: !!token,
    isError 
  };
};