import { useQuery } from '@tanstack/react-query';
import { adminDashboardService } from '../services/adminDashboardService';

export const useDashboardStats = () => {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: adminDashboardService.getAllStats,
    staleTime: 1000 * 60 * 2, // 2 دقیقه کش
  });

  return {
    orders:    data?.orders,
    products:  data?.products,
    financial: data?.financial,
    users:     data?.users,
    expenses:  data?.expenses,
    profit:    data?.profit,
    isLoading,
    isError,
    refetchAll: refetch,
  };
};