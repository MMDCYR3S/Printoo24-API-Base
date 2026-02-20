import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { adminOrderService } from '../services/adminOrderService';

export const useAdminOrderDetails = () => {
  const { id } = useParams();
  const queryClient = useQueryClient();

  // ۱. دریافت اطلاعات سفارش
  const { data: order, isLoading, isError, refetch } = useQuery({
    queryKey: ['admin-order-details', id],
    queryFn: () => adminOrderService.getById(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 2,
  });

  // ۲. ویرایش اطلاعات کلی (مثل تغییر مبلغ کل)
  const updateOrderMutation = useMutation({
    mutationFn: (data) => adminOrderService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-order-details', id] });
      queryClient.invalidateQueries({ queryKey: ['admin-orders'] });
      toast.success('اطلاعات سفارش با موفقیت بروزرسانی شد');
    },
    onError: () => toast.error('خطا در بروزرسانی اطلاعات سفارش'),
  });

  // ۳. تغییر وضعیت سفارش
  const changeStatusMutation = useMutation({
    mutationFn: (data) => adminOrderService.changeStatus(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-order-details', id] });
      queryClient.invalidateQueries({ queryKey: ['admin-orders'] });
      toast.success('وضعیت سفارش تغییر کرد');
    },
    onError: () => toast.error('خطا در تغییر وضعیت'),
  });

  // ۴. حذف یک آیتم از سفارش
  const deleteItemMutation = useMutation({
    mutationFn: (itemId) => adminOrderService.deleteItem(id, itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-order-details', id] });
      toast.success('آیتم با موفقیت از سفارش حذف شد');
    },
    onError: () => toast.error('خطا در حذف آیتم'),
  });

  // ۵. آپلود فایل برای یک آیتم
  const uploadFileMutation = useMutation({
    mutationFn: ({ itemId, formData }) => adminOrderService.uploadItemFile(id, itemId, formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-order-details', id] });
      toast.success('فایل با موفقیت آپلود شد');
    },
    onError: () => toast.error('خطا در آپلود فایل'),
  });

  return {
    orderId: id,
    order,
    isLoading,
    isError,
    refetch,
    updateOrderMutation,
    changeStatusMutation,
    deleteItemMutation,
    uploadFileMutation
  };
};