// src/app/features/admin/customers/hooks/useCustomers.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { customerService } from '../services/customerService';
import { toast } from 'react-hot-toast';

export const useCustomers = () => {
  const queryClient = useQueryClient();

  // فچ کردن دیتا
  const usersQuery = useQuery({
    queryKey: ['admin-customers'],
    queryFn: () => customerService.getAll(),
    staleTime: 1000 * 60 * 5, // 5 دقیقه دیتا تازه میماند
  });

  // ایجاد کاربر
  const createMutation = useMutation({
    mutationFn: customerService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-customers']);
      toast.success('کاربر جدید با موفقیت ایجاد شد');
    },
    onError: (err) => {
      toast.error(err?.response?.data?.message || 'خطا در ایجاد کاربر');
    }
  });

  // ویرایش کاربر
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => customerService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-customers']);
      toast.success('اطلاعات کاربر به‌روز شد');
    },
  });

  // عملیات گروهی: تغییر وضعیت (Optimistic Update)
  const bulkStatusMutation = useMutation({
    mutationFn: customerService.bulkStatus,
    onMutate: async ({ ids, active }) => {
      // کنسل کردن فچ‌های در جریان
      await queryClient.cancelQueries(['admin-customers']);
      const previousData = queryClient.getQueryData(['admin-customers']);

      // آپدیت دستی کش برای سرعت نوری
      queryClient.setQueryData(['admin-customers'], (old) => {
        return old.map(user => 
          ids.includes(user.id) ? { ...user, is_active: active } : user
        );
      });

      return { previousData };
    },
    onError: (err, newTodo, context) => {
      queryClient.setQueryData(['admin-customers'], context.previousData);
      toast.error('خطا در تغییر وضعیت');
    },
    onSettled: () => {
      queryClient.invalidateQueries(['admin-customers']);
    },
  });

  // عملیات گروهی: حذف (Optimistic Update)
  const bulkDeleteMutation = useMutation({
    mutationFn: customerService.bulkDelete,
    onMutate: async (ids) => {
      await queryClient.cancelQueries(['admin-customers']);
      const previousData = queryClient.getQueryData(['admin-customers']);

      queryClient.setQueryData(['admin-customers'], (old) => {
        return old.filter(user => !ids.includes(user.id));
      });

      toast.success(`${ids.length} کاربر حذف شدند`); // فیدبک فوری
      return { previousData };
    },
    onError: (err, ids, context) => {
      queryClient.setQueryData(['admin-customers'], context.previousData);
      toast.error('خطا در حذف کاربران');
    },
    onSettled: () => {
      queryClient.invalidateQueries(['admin-customers']);
    }
  });

  return {
    usersQuery,
    createMutation,
    updateMutation,
    bulkStatusMutation,
    bulkDeleteMutation
  };
};