import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { adminOrderService } from '../services/adminOrderService';

export const useAdminOrderDetails = () => {
  const { id } = useParams();

  const { data: order, isLoading, isError, refetch } = useQuery({
    queryKey: ['admin-order-details', id],
    queryFn: () => adminOrderService.getById(id),
    enabled: !!id, // فقط وقتی آیدی هست اجرا شه
    staleTime: 1000 * 60 * 5, // 5 دقیقه دیتا تازه بمونه
  });

  return {
    order,
    isLoading,
    isError,
    refetch
  };
};