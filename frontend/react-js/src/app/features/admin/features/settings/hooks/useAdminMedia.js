import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminMediaService } from '../../../services/adminMediaService';
import toast from 'react-hot-toast';

export const useAdminMedia = () => {
  const queryClient = useQueryClient();
  const QUERY_KEY = ['admin-site-media'];

  const { data: mediaList = [], isLoading } = useQuery({
    queryKey: QUERY_KEY,
    queryFn: adminMediaService.getAll,
  });

  const createMutation = useMutation({
    mutationFn: adminMediaService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success('رسانه جدید با موفقیت ایجاد شد');
    },
    onError: () => toast.error('خطا در آپلود رسانه'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => adminMediaService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success('تغییرات با موفقیت ذخیره شد');
    },
    onError: () => toast.error('خطا در ثبت تغییرات'),
  });

  const deleteMutation = useMutation({
    mutationFn: adminMediaService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success('رسانه با موفقیت حذف شد');
    },
    onError: () => toast.error('خطا در حذف رسانه'),
  });

  return { mediaList, isLoading, createMutation, updateMutation, deleteMutation };
};