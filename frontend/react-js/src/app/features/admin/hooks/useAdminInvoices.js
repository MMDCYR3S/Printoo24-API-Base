import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { adminInvoiceService } from '../services/adminInvoiceService';

export const useAdminInvoices = (orderId) => {
  const queryClient = useQueryClient();
  const queryKey = ['order-invoice', orderId];

  // دریافت فاکتور
  const { data: invoice, isLoading, isError, refetch } = useQuery({
    queryKey,
    queryFn: () => adminInvoiceService.getByOrderId(orderId),
    enabled: !!orderId,
    retry: false,
  });

  // ۱. ایجاد فاکتور جدید
  const createMutation = useMutation({
    mutationFn: adminInvoiceService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      toast.success('فاکتور جدید صادر شد');
    },
    onError: () => toast.error('خطا در صدور فاکتور')
  });

  // ۲. ویرایش فیلدهای مالی و اطلاعاتی
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => adminInvoiceService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      toast.success('تغییرات مالی با موفقیت اعمال شد');
    },
    onError: () => toast.error('خطا در بروزرسانی مبالغ')
  });

  // ۳. نهایی‌سازی (Approve/Finalize)
  const approveMutation = useMutation({
    mutationFn: adminInvoiceService.approve,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      toast.success('فاکتور نهایی و وضعیت آن قفل شد');
    },
    onError: () => toast.error('خطا در نهایی‌سازی فاکتور')
  });

  // ۴. تغییر وضعیت دستی (PENDING, PAID_FULL, etc.)
  const changeStatusMutation = useMutation({
    mutationFn: ({ id, status }) => adminInvoiceService.changeStatus(id, status),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey });
      toast.success(`وضعیت به ${variables.status} تغییر یافت`);
    },
    onError: () => toast.error('خطا در تغییر وضعیت فاکتور')
  });

  // ۵. حذف کامل فاکتور
  const deleteMutation = useMutation({
    mutationFn: adminInvoiceService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      toast.success('فاکتور از سیستم حذف شد');
    },
    onError: () => toast.error('خطا در حذف فاکتور')
  });

  return {
    invoice,
    isLoading,
    isError,
    // Mutations
    createMutation,
    updateMutation,
    approveMutation,
    changeStatusMutation, // این همونیه که جا افتاده بود
    deleteMutation,
    refetch
  };
};