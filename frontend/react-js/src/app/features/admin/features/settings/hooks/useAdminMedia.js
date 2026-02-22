import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminMediaService } from '../../../services/adminMediaService';
import toast from 'react-hot-toast';

export const useAdminMedia = () => {
  const queryClient = useQueryClient();
  const QUERY_KEY = ['admin-site-media'];

  // دریافت لیست رسانه‌ها
  const { data: mediaList = [], isLoading } = useQuery({
    queryKey: QUERY_KEY,
    queryFn: adminMediaService.getAll,
  });

  // ایجاد رسانه جدید
  const createMutation = useMutation({
    mutationFn: adminMediaService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success('رسانه جدید با موفقیت افزوده شد');
    },
    onError: () => toast.error('خطا در ایجاد رسانه'),
  });

  // ویرایش رسانه (و تغییر وضعیت فعال/غیرفعال)
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => adminMediaService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success('تغییرات با موفقیت ذخیره شد');
    },
    onError: () => toast.error('خطا در ثبت تغییرات'),
  });

  // حذف رسانه
  const deleteMutation = useMutation({
    mutationFn: adminMediaService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success('رسانه حذف شد');
    },
    onError: () => toast.error('خطا در حذف رسانه'),
  });

  return {
    mediaList,
    isLoading,
    createMutation,
    updateMutation,
    deleteMutation,
  };
};