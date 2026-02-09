// src/app/features/settings/hooks/useAdminModals.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminModalService } from '../../../services/adminModalService';
import toast from 'react-hot-toast';

export const useAdminModals = () => {
  const queryClient = useQueryClient();

  const { data: modals = [], isLoading } = useQuery({
    queryKey: ['admin-modals'],
    queryFn: adminModalService.getAll,
  });

  const createMutation = useMutation({
    mutationFn: adminModalService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-modals']);
      toast.success('مودال جدید ایجاد شد');
    },
    onError: () => toast.error('خطا در ایجاد مودال'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => adminModalService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-modals']);
      toast.success('مودال ویرایش شد');
    },
    onError: () => toast.error('خطا در ویرایش'),
  });

  const deleteMutation = useMutation({
    mutationFn: adminModalService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-modals']);
      toast.success('مودال حذف شد');
    },
  });

  const toggleStatusMutation = useMutation({
    mutationFn: adminModalService.toggleStatus,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-modals']);
      toast.success('وضعیت تغییر کرد');
    },
    onError: () => toast.error('خطا در تغییر وضعیت'),
  });

  return {
    modals,
    isLoading,
    createMutation,
    updateMutation,
    deleteMutation,
    toggleStatusMutation,
  };
};