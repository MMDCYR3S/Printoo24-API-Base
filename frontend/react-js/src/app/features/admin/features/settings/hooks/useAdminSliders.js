// src/app/features/settings/hooks/useAdminSliders.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminSliderService } from '../../../services/adminSliderService';
import toast from 'react-hot-toast';

export const useAdminSliders = () => {
  const queryClient = useQueryClient();

  // دریافت لیست
  const { data: sliders = [], isLoading } = useQuery({
    queryKey: ['admin-sliders'],
    queryFn: adminSliderService.getAll,
  });

  // حذف
  const deleteMutation = useMutation({
    mutationFn: adminSliderService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-sliders']);
      toast.success('اسلایدر حذف شد');
    },
    onError: () => toast.error('خطا در حذف اسلایدر'),
  });

  // ایجاد
  const createMutation = useMutation({
    mutationFn: adminSliderService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-sliders']);
      toast.success('اسلایدر جدید افزوده شد');
    },
    onError: () => toast.error('خطا در ایجاد اسلایدر'),
  });

  // ویرایش
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => adminSliderService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-sliders']);
      toast.success('تغییرات ذخیره شد');
    },
    onError: () => toast.error('خطا در ویرایش'),
  });

  return {
    sliders,
    isLoading,
    deleteMutation,
    createMutation,
    updateMutation,
  };
};