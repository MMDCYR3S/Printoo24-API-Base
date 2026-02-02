import { useQuery } from '@tanstack/react-query';
import { adminDashboardService } from '../services/adminDashboardService';

export const useDashboardStats = () => {
  // دریافت آمار سفارشات
  const ordersQuery = useQuery({
    queryKey: ['dashboard-orders'],
    queryFn: adminDashboardService.getOrderStats,
    staleTime: 1000 * 60 * 5, // 5 دقیقه
  });

  // دریافت آمار محصولات
  const productsQuery = useQuery({
    queryKey: ['dashboard-products'],
    queryFn: adminDashboardService.getProductStats,
    staleTime: 1000 * 60 * 10,
  });

  // دریافت آمار مالی
  const financialQuery = useQuery({
    queryKey: ['dashboard-financial'],
    queryFn: adminDashboardService.getFinancialStats,
    staleTime: 1000 * 60 * 5,
  });

  // دریافت آمار کاربران
  const usersQuery = useQuery({
    queryKey: ['dashboard-users'],
    queryFn: adminDashboardService.getUserStats,
    staleTime: 1000 * 60 * 10,
  });

  const isLoading = 
    ordersQuery.isLoading || 
    productsQuery.isLoading || 
    financialQuery.isLoading || 
    usersQuery.isLoading;

  const isError = 
    ordersQuery.isError || 
    productsQuery.isError || 
    financialQuery.isError || 
    usersQuery.isError;

  // تابع رفرش کلی
  const refetchAll = () => {
    ordersQuery.refetch();
    productsQuery.refetch();
    financialQuery.refetch();
    usersQuery.refetch();
  };

  return {
    orders: ordersQuery.data,
    products: productsQuery.data,
    financial: financialQuery.data,
    users: usersQuery.data,
    isLoading,
    isError,
    refetchAll
  };
};